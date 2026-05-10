from datetime import UTC, datetime, timedelta

import pytest

from backend.app.lead_automation.service.audit_service import AuditPayloadLeakError, assert_audit_payload_safe
from backend.app.lead_automation.service.business_service import _mask_email, _mask_phone
from backend.app.lead_automation.service.cleaner_service import clean_raw_record, normalize_email, normalize_phone
from backend.app.lead_automation.service.dedupe_service import InMemoryLeadStore, upsert_lead
from backend.app.lead_automation.service.export_service import build_csv_export
from backend.app.lead_automation.service.firecrawl_client import FirecrawlClient, FirecrawlHTTPError, FirecrawlTransportError
from backend.app.lead_automation.service.provider_registry import PROVIDERS, CrawlRequest, get_provider
from backend.app.lead_automation.service.retention_service import archive_expired_contacts
from backend.app.lead_automation.service.scoring_service import score_cleaned_lead


def test_normalize_email_handles_gmail_rules_and_preserves_outlook_dots() -> None:
    assert normalize_email(' First.Last+sales@GoogleMail.com ') == 'firstlast@gmail.com'
    assert normalize_email('first.last+sales@outlook.com') == 'first.last@outlook.com'
    assert normalize_email('test@example.com') is None


def test_normalize_phone_outputs_e164_for_cn_us_and_rejects_invalid() -> None:
    assert normalize_phone('138 1234 5678', country_hint='CN') == '+8613812345678'
    assert normalize_phone('(415) 555-2671', country_hint='US') == '+14155552671'
    assert normalize_phone('020 7946 0018', country_hint='GB') == '+442079460018'
    assert normalize_phone('abc', country_hint='CN') is None


def test_cleaner_prefers_structured_payload_and_default_accepts_email_or_phone() -> None:
    cleaned = clean_raw_record(
        {
            'structured_payload': {
                'company_name': 'Acme Ltd',
                'emails': [' Sales.Team+cn@gmail.com '],
                'phones': [],
                'website': 'https://acme.example',
            },
            'markdown': 'Contact Sales.Team+cn@gmail.com',
            'source_url': 'https://acme.example/contact',
            'source_type': 'public_web',
        },
        min_contact_fields=['email', 'phone'],
        country_hint='CN',
    )

    assert cleaned.accepted is True
    assert cleaned.rejected_reason is None
    assert cleaned.email_normalized == 'salesteam@gmail.com'
    assert cleaned.phone_normalized is None
    assert cleaned.metadata['email_candidates'] == [' Sales.Team+cn@gmail.com ']


@pytest.mark.parametrize(
    ('min_fields', 'expected_reason'),
    [
        (['email', 'phone'], 'missing_contact'),
        (['email'], 'missing_email'),
        (['phone'], 'missing_phone'),
    ],
)
def test_cleaner_rejected_reason_follows_min_contact_fields(min_fields: list[str], expected_reason: str) -> None:
    cleaned = clean_raw_record(
        {
            'structured_payload': {'company_name': 'No Contact Inc'},
            'markdown': 'No public contact here.',
            'source_url': 'https://nocontact.example',
            'source_type': 'public_web',
        },
        min_contact_fields=min_fields,
        country_hint='CN',
    )

    assert cleaned.accepted is False
    assert cleaned.rejected_reason == expected_reason


def test_scoring_is_deterministic_and_rewards_traceable_contact_data() -> None:
    cleaned = clean_raw_record(
        {
            'structured_payload': {
                'company_name': 'Score Co',
                'emails': ['hello@score.co'],
                'phones': ['(415) 555-2671'],
                'website': 'https://score.co',
                'address': '1 Market St',
                'industry': 'SaaS',
            },
            'markdown': 'hello@score.co (415) 555-2671 1 Market St',
            'source_url': 'https://score.co/contact',
            'source_type': 'public_web',
            'llm_confidence': 0.91,
        },
        min_contact_fields=['email', 'phone'],
        country_hint='US',
    )

    assert score_cleaned_lead(cleaned) == 100


def test_dedupe_uses_email_phone_domain_order_and_scope_isolation() -> None:
    store = InMemoryLeadStore()
    first = clean_raw_record(
        {
            'structured_payload': {'company_name': 'Same Co', 'emails': ['sales@example.org']},
            'source_url': 'https://example.org/contact',
            'source_type': 'public_web',
        },
        min_contact_fields=['email', 'phone'],
        country_hint='US',
    )
    inserted = upsert_lead(store, first, lead_scope='public', user_id=None, keyword='crm')

    second = clean_raw_record(
        {
            'structured_payload': {'company_name': 'Same Co other', 'phones': ['(415) 555-2671'], 'website': 'https://example.org'},
            'source_url': 'https://example.org/about',
            'source_type': 'public_web',
        },
        min_contact_fields=['email', 'phone'],
        country_hint='US',
    )
    duplicate_by_domain = upsert_lead(store, second, lead_scope='public', user_id=None, keyword='crm')
    user_pool_insert = upsert_lead(store, first, lead_scope='user', user_id=7, keyword='crm')

    assert inserted.created is True
    assert duplicate_by_domain.created is False
    assert duplicate_by_domain.match_dimension == 'domain'
    assert user_pool_insert.created is True
    assert len(store.contacts) == 2


def test_provider_registry_contains_five_sources_and_rejects_unknown() -> None:
    assert {'maps', 'yellow_pages', 'social_media', 'b2b', 'public_web'} <= set(PROVIDERS)
    provider = get_provider('public_web')
    assert provider.source_type == 'public_web'

    with pytest.raises(KeyError):
        get_provider('unknown')


@pytest.mark.asyncio
async def test_provider_returns_crawled_items_from_firecrawl_client() -> None:
    class FakeFirecrawl:
        async def scrape_lead_json(self, url: str, schema_version: str, prompt_version: str):
            return {
                'source_url': url,
                'title': 'Public web result',
                'markdown': 'sales@example.com',
                'structured_payload': {'emails': ['sales@example.com']},
                'extract_mode': 'scrape_json',
                'llm_schema_version': schema_version,
                'llm_prompt_version': prompt_version,
                'attempt_count': 1,
            }

    provider = get_provider('public_web')
    items = await provider.crawl(
        CrawlRequest(job_id=1, keyword='example.com', source_type='public_web', lead_scope='public'),
        firecrawl_client=FakeFirecrawl(),
    )

    assert len(items) == 1
    assert items[0].source_url == 'https://example.com'
    assert items[0].structured_payload == {'emails': ['sales@example.com']}


@pytest.mark.asyncio
async def test_firecrawl_retries_only_retryable_failures() -> None:
    calls: list[str] = []

    async def sender(method: str, url: str, payload: dict, headers: dict, timeout: float):
        calls.append(url)
        if len(calls) == 1:
            raise FirecrawlTransportError('timeout')
        return {'status_code': 200, 'json': {'markdown': 'ok', 'metadata': {'title': 'Ok'}}}

    client = FirecrawlClient(api_key='secret', sender=sender, sleep=lambda _: None, jitter=lambda: 0)
    result = await client.scrape_markdown('https://example.com')

    assert result['markdown'] == 'ok'
    assert result['attempt_count'] == 2
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_firecrawl_does_not_retry_non_retryable_4xx() -> None:
    calls = 0

    async def sender(method: str, url: str, payload: dict, headers: dict, timeout: float):
        nonlocal calls
        calls += 1
        return {'status_code': 404, 'json': {'error': 'not found'}}

    client = FirecrawlClient(sender=sender, sleep=lambda _: None)

    with pytest.raises(FirecrawlHTTPError) as exc_info:
        await client.scrape_markdown('https://example.com/missing')

    assert calls == 1
    assert exc_info.value.status_code == 404


def test_audit_payload_rejects_plaintext_pii_but_allows_hashes() -> None:
    assert_audit_payload_safe({'target_emails_sha256': ['a' * 64], 'total_count': 1})

    with pytest.raises(AuditPayloadLeakError):
        assert_audit_payload_safe({'email': 'foo@example.com'})

    with pytest.raises(AuditPayloadLeakError):
        assert_audit_payload_safe({'phone': '+14155552671'})


def test_export_writes_csv_snapshot_and_safe_audit_payload() -> None:
    contacts = [
        {'id': 1, 'lead_no': 'L001', 'company_name': 'Export Co', 'email': 'sales@export.co', 'phone': '+14155552671'},
    ]
    export = build_csv_export(
        contacts,
        batch_no='EXP001',
        user_id=9,
        filter_payload={'keyword': 'export'},
        now=datetime(2026, 5, 10, tzinfo=UTC),
    )

    assert export.batch['total_count'] == 1
    assert export.items[0]['snapshot']['email'] == 'sales@export.co'
    assert 'sales@export.co' in export.csv_text
    assert export.audit_log['event_type'] == 'export'
    assert 'sales@export.co' not in str(export.audit_log['payload'])


def test_archive_expired_contacts_anonymizes_uncontacted_only() -> None:
    now = datetime(2026, 5, 10, tzinfo=UTC)
    contacts = [
        {
            'id': 1,
            'status': 'new',
            'archived_at': now - timedelta(days=1),
            'email': 'old@example.com',
            'email_normalized': 'old@example.com',
            'phone': '+14155552671',
            'phone_normalized': '+14155552671',
        },
        {
            'id': 2,
            'status': 'contacted',
            'archived_at': now - timedelta(days=1),
            'email': 'keep@example.com',
            'email_normalized': 'keep@example.com',
            'phone': '+14155552672',
            'phone_normalized': '+14155552672',
        },
    ]

    archived = archive_expired_contacts(contacts, now=now)

    assert archived == 1
    assert contacts[0]['status'] == 'archived'
    assert contacts[0]['email'] is None
    assert contacts[0]['phone_normalized'] is None
    assert contacts[1]['email'] == 'keep@example.com'


def test_pii_masking_for_business_list_views() -> None:
    assert _mask_email('sales@example.com') == 's***@example.com'
    assert _mask_email(None) is None
    assert _mask_phone('+8613812345678') == '+861****5678'
    assert _mask_phone(None) is None
