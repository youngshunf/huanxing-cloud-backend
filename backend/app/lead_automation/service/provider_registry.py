from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class CrawlRequest:
    job_id: int
    keyword: str
    source_type: str
    lead_scope: str
    user_id: int | None = None
    max_pages: int = 5
    max_results: int = 100
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CrawledItem:
    source_type: str
    source_url: str | None = None
    title: str | None = None
    markdown: str | None = None
    raw_text: str | None = None
    raw_html: str | None = None
    raw_payload: dict[str, Any] | None = None
    structured_payload: dict[str, Any] | None = None
    llm_confidence: float | None = None
    extract_mode: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    firecrawl_request_id: int | None = None


class FirecrawlLike(Protocol):
    async def scrape_lead_json(self, url: str, schema_version: str, prompt_version: str) -> dict[str, Any]: ...
    async def extract_leads(self, urls: list[str], schema_version: str, prompt_version: str) -> dict[str, Any]: ...


class BaseProvider:
    source_type = ''

    async def crawl(self, request: CrawlRequest, *, firecrawl_client: FirecrawlLike) -> list[CrawledItem]:
        url = self._keyword_to_url(request.keyword)
        options = request.config.get('firecrawl_options', {})
        schema_version = options.get('schema_version', 'lead_v1')
        prompt_version = options.get('prompt_version', 'lead_extract_v1')
        if options.get('extract_mode') == 'extract':
            result = await firecrawl_client.extract_leads([url], schema_version, prompt_version)
        else:
            result = await firecrawl_client.scrape_lead_json(url, schema_version, prompt_version)
        return [
            CrawledItem(
                source_type=self.source_type,
                source_url=result.get('source_url') or url,
                title=result.get('title'),
                markdown=result.get('markdown'),
                raw_text=result.get('raw_text'),
                raw_html=result.get('raw_html'),
                raw_payload=result.get('raw_payload') or result,
                structured_payload=result.get('structured_payload'),
                llm_confidence=result.get('llm_confidence'),
                extract_mode=result.get('extract_mode'),
                metadata={
                    'llm_schema_version': result.get('llm_schema_version'),
                    'llm_prompt_version': result.get('llm_prompt_version'),
                    'attempt_count': result.get('attempt_count'),
                },
            )
        ]

    def _keyword_to_url(self, keyword: str) -> str:
        if keyword.startswith(('http://', 'https://')):
            return keyword
        return f'https://{keyword.strip("/")}'


PROVIDERS: dict[str, BaseProvider] = {}


def register(source_type: str):
    def decorator(cls: type[BaseProvider]) -> type[BaseProvider]:
        instance = cls()
        instance.source_type = source_type
        PROVIDERS[source_type] = instance
        return cls

    return decorator


def get_provider(source_type: str) -> BaseProvider:
    return PROVIDERS[source_type]


@register('maps')
class MapsProvider(BaseProvider):
    pass


@register('yellow_pages')
class YellowPagesProvider(BaseProvider):
    pass


@register('social_media')
class SocialMediaProvider(BaseProvider):
    pass


@register('b2b')
class B2BProvider(BaseProvider):
    pass


@register('public_web')
class PublicWebProvider(BaseProvider):
    pass
