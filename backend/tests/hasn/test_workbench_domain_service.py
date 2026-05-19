from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import httpx
import pytest
import pytest_asyncio
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.common.exception import errors

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class _Base(DeclarativeBase):
    pass


class EnterpriseStub(_Base):
    __tablename__ = 'hasn_enterprise'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(128), default='')
    slug: Mapped[str] = mapped_column(sa.String(64), default='', unique=True)
    logo: Mapped[str | None] = mapped_column(sa.String(512), default=None)
    description: Mapped[str | None] = mapped_column(sa.Text, default=None)
    owner_user_id: Mapped[int] = mapped_column(sa.Integer, default=0)
    join_policy: Mapped[str] = mapped_column(sa.String(16), default='invite_only')
    status: Mapped[str] = mapped_column(sa.String(16), default='active')


class MembershipStub(_Base):
    __tablename__ = 'hasn_enterprise_membership'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int] = mapped_column(sa.Integer, default=0)
    user_id: Mapped[int] = mapped_column(sa.Integer, default=0)
    role: Mapped[str] = mapped_column(sa.String(16), default='member')
    status: Mapped[str] = mapped_column(sa.String(16), default='pending')
    apply_message: Mapped[str | None] = mapped_column(sa.Text, default=None)
    apply_via: Mapped[str | None] = mapped_column(sa.String(16), default=None)
    invite_code: Mapped[str | None] = mapped_column(sa.String(32), default=None)
    decided_by: Mapped[int | None] = mapped_column(sa.Integer, default=None)
    decided_at: Mapped[str | None] = mapped_column(sa.String(64), default=None)
    decision_note: Mapped[str | None] = mapped_column(sa.Text, default=None)


class InviteCodeStub(_Base):
    __tablename__ = 'hasn_enterprise_invite_code'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int] = mapped_column(sa.Integer, default=0)
    code: Mapped[str] = mapped_column(sa.String(32), default='', unique=True)
    created_by: Mapped[int] = mapped_column(sa.Integer, default=0)
    max_uses: Mapped[int | None] = mapped_column(sa.Integer, default=None)
    used_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    expires_at: Mapped[str | None] = mapped_column(sa.String(64), default=None)
    auto_approve: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    revoked: Mapped[bool] = mapped_column(sa.Boolean, default=False)


class ActiveWorkspaceStub(_Base):
    __tablename__ = 'hasn_user_active_workspace'

    user_id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(sa.String(16), default='personal')
    enterprise_id: Mapped[int | None] = mapped_column(sa.Integer, default=None)


class WorkspaceAppStub(_Base):
    __tablename__ = 'hasn_workspace_app'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    workspace_kind: Mapped[str] = mapped_column(sa.String(16), default='personal')
    user_id: Mapped[int | None] = mapped_column(sa.Integer, default=None)
    enterprise_id: Mapped[int | None] = mapped_column(sa.Integer, default=None)
    app_id: Mapped[str] = mapped_column(sa.String(64), default='')
    status: Mapped[str] = mapped_column(sa.String(16), default='active')
    config: Mapped[dict] = mapped_column(sa.JSON, default=dict)
    enabled_by: Mapped[int | None] = mapped_column(sa.Integer, default=None)


class RagflowInstanceStub(_Base):
    __tablename__ = 'hasn_ragflow_instance'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(sa.String(16), default='public')
    enterprise_id: Mapped[int | None] = mapped_column(sa.Integer, default=None)
    url: Mapped[str] = mapped_column(sa.String(512), default='')
    admin_api_key_encrypted: Mapped[bytes] = mapped_column(sa.LargeBinary, default=b'')
    public_pem: Mapped[str] = mapped_column(sa.Text, default='')
    default_embd_id: Mapped[str | None] = mapped_column(sa.String(128), default=None)
    default_llm_id: Mapped[str | None] = mapped_column(sa.String(128), default=None)
    status: Mapped[str] = mapped_column(sa.String(16), default='pending_config')


class RagflowCredentialStub(_Base):
    __tablename__ = 'hasn_ragflow_credential'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, default=0)
    instance_id: Mapped[int] = mapped_column(sa.Integer, default=0)
    ragflow_user_id: Mapped[str] = mapped_column(sa.String(64), default='')
    ragflow_tenant_id: Mapped[str] = mapped_column(sa.String(64), default='')
    api_key_encrypted: Mapped[bytes] = mapped_column(sa.LargeBinary, default=b'')
    status: Mapped[str] = mapped_column(sa.String(16), default='pending')
    last_error: Mapped[str | None] = mapped_column(sa.Text, default=None)


class CapturingBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    async def publish(self, event_name: str, payload: dict) -> None:
        self.events.append((event_name, payload))


class CapturingProvisioningService:
    def __init__(self) -> None:
        self.provisioned: list[tuple[int, int]] = []

    async def provision_one(self, user_id: int, instance_id: int) -> None:
        self.provisioned.append((user_id, instance_id))
        return


class CapturingRAGFlowClient:
    def __init__(self, base_url: str, calls: list[tuple[str, str, dict]]) -> None:
        self.base_url = base_url
        self.calls = calls

    async def get(self, path: str, *, params=None, headers=None):
        self.calls.append(('GET', path, {'params': params, 'headers': headers}))
        if path == '/api/v1/datasets':
            return {
                'code': 0,
                'data': [
                    {'id': 'ds-1', 'name': 'Enterprise KB', 'document_count': 1},
                ],
            }
        if path == '/api/v1/datasets/ds-1/documents':
            return {
                'code': 0,
                'data': {
                    'docs': [
                        {'id': 'doc-1', 'name': 'Runbook.txt', 'dataset_id': 'ds-1'},
                    ],
                },
            }
        raise AssertionError(f'unexpected GET {path}')

    async def post(self, path: str, *, json=None, headers=None):
        self.calls.append(('POST', path, {'json': json, 'headers': headers}))
        if path == '/api/v1/datasets/ds-1/search':
            return {
                'code': 0,
                'data': {
                    'chunks': [
                        {
                            'id': 'chunk-1',
                            'document_id': 'doc-1',
                            'document_name': 'Runbook.txt',
                            'content': 'rotate enterprise credentials safely',
                            'dataset_id': 'ds-1',
                        },
                    ],
                    'total': 1,
                },
            }
        if path == '/api/v1/datasets/ds-1/documents?type=empty':
            return {
                'code': 0,
                'data': [
                    {'id': 'doc-new', 'name': json['name'], 'dataset_id': 'ds-1'},
                ],
            }
        if path == '/api/v1/datasets/ds-1/documents/doc-new/chunks':
            return {
                'code': 0,
                'data': {'chunk': {'id': 'chunk-new', 'content': json['content']}},
            }
        raise AssertionError(f'unexpected POST {path}')


class ExpiringRAGFlowClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def post(self, path: str, *, json=None, headers=None):
        self.calls.append({'path': path, 'json': json, 'headers': headers})
        if len(self.calls) == 1:
            request = httpx.Request('POST', f'https://knowledge.example{path}')
            response = httpx.Response(401, request=request)
            raise httpx.HTTPStatusError('unauthorized', request=request, response=response)
        return {
            'code': 0,
            'data': {
                'chunks': [
                    {
                        'id': 'chunk-1',
                        'document_id': 'doc-1',
                        'document_name': 'Runbook.txt',
                        'content': 'fresh token search result',
                        'dataset_id': 'ds-1',
                    },
                ],
                'total': 1,
            },
        }


class RefreshingProvisioningService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.provisioned: list[tuple[int, int]] = []

    async def provision_one(self, user_id: int, instance_id: int):
        self.provisioned.append((user_id, instance_id))
        credential = (
            await self.db.execute(
                sa.select(RagflowCredentialStub).where(
                    RagflowCredentialStub.user_id == user_id,
                    RagflowCredentialStub.instance_id == instance_id,
                )
            )
        ).scalar_one()
        credential.api_key_encrypted = b'fresh-token'
        credential.status = 'active'
        await self.db.flush()
        return credential


@pytest_asyncio.fixture
async def db_session(monkeypatch) -> AsyncGenerator[AsyncSession, None]:
    import backend.app.hasn.service.workbench_domain_service as service_mod

    replacements = {
        'HasnEnterprise': EnterpriseStub,
        'HasnEnterpriseMembership': MembershipStub,
        'HasnEnterpriseInviteCode': InviteCodeStub,
        'HasnUserActiveWorkspace': ActiveWorkspaceStub,
        'HasnWorkspaceApp': WorkspaceAppStub,
        'HasnRagflowInstance': RagflowInstanceStub,
        'HasnRagflowCredential': RagflowCredentialStub,
    }
    for name, replacement in replacements.items():
        monkeypatch.setattr(service_mod, name, replacement, raising=True)

    monkeypatch.setattr(
        service_mod,
        'decrypt_ragflow_secret',
        lambda value: value.decode('utf-8') if isinstance(value, bytes) else value,
    )

    engine = create_async_engine('sqlite+aiosqlite:///:memory:', future=True)
    async with engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


def _service(enterprise_bus: CapturingBus | None = None, workbench_bus: CapturingBus | None = None):
    from backend.app.hasn.service.workbench_domain_service import WorkbenchDomainService

    return WorkbenchDomainService(
        enterprise_bus=enterprise_bus or CapturingBus(),
        workbench_bus=workbench_bus or CapturingBus(),
    )


def _ragflow_service(calls: list[tuple[str, str, dict]]):
    from backend.app.hasn.service.workbench_domain_service import WorkbenchDomainService

    return WorkbenchDomainService(
        enterprise_bus=CapturingBus(),
        workbench_bus=CapturingBus(),
        ragflow_client_factory=lambda base_url: CapturingRAGFlowClient(base_url, calls),
    )


async def _seed_active_ragflow_workspace(db_session: AsyncSession) -> tuple[int, int]:
    db_session.add(EnterpriseStub(name='Acme', slug='acme', owner_user_id=11, status='active'))
    await db_session.flush()
    enterprise_id = 1
    db_session.add_all([
        MembershipStub(enterprise_id=enterprise_id, user_id=12, role='member', status='approved'),
        ActiveWorkspaceStub(user_id=12, kind='enterprise', enterprise_id=enterprise_id),
        RagflowInstanceStub(
            scope='enterprise',
            enterprise_id=enterprise_id,
            url='https://knowledge.example',
            public_pem='pem',
            status='active',
        ),
    ])
    await db_session.flush()
    instance_id = 1
    db_session.add(
        RagflowCredentialStub(
            user_id=12,
            instance_id=instance_id,
            ragflow_user_id='u-12',
            ragflow_tenant_id='t-12',
            api_key_encrypted=b'ragflow-user-token',
            status='active',
        )
    )
    await db_session.flush()
    return enterprise_id, instance_id


@pytest.mark.asyncio
async def test_create_enterprise_approves_owner_and_installs_knowledge(db_session: AsyncSession) -> None:
    bus = CapturingBus()
    service = _service(enterprise_bus=bus)

    enterprise = await service.create_enterprise(
        db_session,
        user_id=11,
        name='Acme',
        slug='acme',
        description='Ops',
        join_policy='invite_only',
    )

    assert enterprise['id'] == 1
    assert bus.events == [('on_enterprise_created', {'enterprise_id': 1, 'owner_user_id': 11})]

    owner = (await db_session.execute(sa.select(MembershipStub).where(MembershipStub.enterprise_id == 1))).scalar_one()
    assert (owner.user_id, owner.role, owner.status) == (11, 'owner', 'approved')

    app = (
        await db_session.execute(sa.select(WorkspaceAppStub).where(WorkspaceAppStub.enterprise_id == 1))
    ).scalar_one()
    assert (app.workspace_kind, app.app_id, app.status, app.enabled_by) == ('enterprise', 'knowledge', 'active', 11)


@pytest.mark.asyncio
async def test_invite_auto_approve_switches_active_workspace_and_invalidates_used_code(
    db_session: AsyncSession,
) -> None:
    bus = CapturingBus()
    service = _service(enterprise_bus=bus)
    enterprise = await service.create_enterprise(
        db_session,
        user_id=11,
        name='Acme',
        slug='acme',
    )
    invite = await service.create_invite_code(
        db_session,
        enterprise_id=enterprise['id'],
        created_by=11,
        code='JOIN-1',
        max_uses=1,
        auto_approve=True,
    )

    application = await service.apply_enterprise(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=12,
        apply_message='let me in',
        invite_code=invite['code'],
    )
    active = await service.switch_active_workspace(
        db_session,
        user_id=12,
        kind='enterprise',
        enterprise_id=enterprise['id'],
    )
    workspaces = await service.list_user_workspaces(db_session, user_id=12)

    assert application['status'] == 'approved'
    assert active['kind'] == 'enterprise'
    assert active['enterprise_id'] == enterprise['id']
    assert [workspace['kind'] for workspace in workspaces['available']] == ['personal', 'enterprise']
    assert ('on_member_approved', {'enterprise_id': enterprise['id'], 'user_id': 12}) in bus.events
    assert (
        'on_workspace_switched',
        {
            'user_id': 12,
            'prev_workspace': {'kind': 'personal', 'enterprise_id': None},
            'next_workspace': {'kind': 'enterprise', 'enterprise_id': enterprise['id']},
        },
    ) in bus.events

    with pytest.raises(errors.RequestError, match='invite_code_used_up'):
        await service.apply_enterprise(
            db_session,
            enterprise_id=enterprise['id'],
            user_id=13,
            apply_message=None,
            invite_code=invite['code'],
        )


@pytest.mark.asyncio
async def test_invite_codes_reject_revoked_and_expired_codes(db_session: AsyncSession) -> None:
    service = _service()
    enterprise = await service.create_enterprise(
        db_session,
        user_id=11,
        name='Acme',
        slug='acme',
    )
    revoked = await service.create_invite_code(
        db_session,
        enterprise_id=enterprise['id'],
        created_by=11,
        code='REVOKED',
        auto_approve=True,
    )
    await service.revoke_invite_code(
        db_session,
        enterprise_id=enterprise['id'],
        code=revoked['code'],
    )
    expired = await service.create_invite_code(
        db_session,
        enterprise_id=enterprise['id'],
        created_by=11,
        code='EXPIRED',
        expires_at=service_mod_timezone_now_minus_one_day(),
        auto_approve=True,
    )

    with pytest.raises(errors.RequestError, match='invite_code_revoked'):
        await service.apply_enterprise(
            db_session,
            enterprise_id=enterprise['id'],
            user_id=12,
            apply_message=None,
            invite_code=revoked['code'],
        )
    with pytest.raises(errors.RequestError, match='invite_code_expired'):
        await service.apply_enterprise(
            db_session,
            enterprise_id=enterprise['id'],
            user_id=13,
            apply_message=None,
            invite_code=expired['code'],
        )


@pytest.mark.asyncio
async def test_remove_current_enterprise_member_falls_back_to_personal_and_emits_hooks(
    db_session: AsyncSession,
) -> None:
    bus = CapturingBus()
    service = _service(enterprise_bus=bus)
    enterprise = await service.create_enterprise(
        db_session,
        user_id=11,
        name='Acme',
        slug='acme',
    )
    invite = await service.create_invite_code(
        db_session,
        enterprise_id=enterprise['id'],
        created_by=11,
        code='JOIN-2',
        auto_approve=True,
    )
    await service.apply_enterprise(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=12,
        apply_message=None,
        invite_code=invite['code'],
    )
    await service.switch_active_workspace(
        db_session,
        user_id=12,
        kind='enterprise',
        enterprise_id=enterprise['id'],
    )

    await service.remove_member(db_session, enterprise_id=enterprise['id'], user_id=12)

    active = await service.get_active_workspace(db_session, user_id=12)
    membership = (
        await db_session.execute(
            sa.select(MembershipStub).where(
                MembershipStub.enterprise_id == enterprise['id'],
                MembershipStub.user_id == 12,
            )
        )
    ).scalar_one()
    assert active == {'kind': 'personal', 'enterprise_id': None}
    assert membership.status == 'left'
    assert (
        'on_workspace_switched',
        {
            'user_id': 12,
            'prev_workspace': {'kind': 'enterprise', 'enterprise_id': enterprise['id']},
            'next_workspace': {'kind': 'personal', 'enterprise_id': None},
        },
    ) in bus.events
    assert ('on_member_left', {'enterprise_id': enterprise['id'], 'user_id': 12}) in bus.events


@pytest.mark.asyncio
async def test_delete_enterprise_falls_back_all_active_members_and_emits_disband_hook(
    db_session: AsyncSession,
) -> None:
    bus = CapturingBus()
    service = _service(enterprise_bus=bus)
    enterprise = await service.create_enterprise(
        db_session,
        user_id=11,
        name='Acme',
        slug='acme',
    )
    for user_id in (12, 13):
        invite = await service.create_invite_code(
            db_session,
            enterprise_id=enterprise['id'],
            created_by=11,
            code=f'JOIN-{user_id}',
            auto_approve=True,
        )
        await service.apply_enterprise(
            db_session,
            enterprise_id=enterprise['id'],
            user_id=user_id,
            apply_message=None,
            invite_code=invite['code'],
        )
        await service.switch_active_workspace(
            db_session,
            user_id=user_id,
            kind='enterprise',
            enterprise_id=enterprise['id'],
        )

    await service.delete_enterprise(db_session, enterprise_id=enterprise['id'])

    assert await service.get_active_workspace(db_session, user_id=11) == {
        'kind': 'personal',
        'enterprise_id': None,
    }
    assert await service.get_active_workspace(db_session, user_id=12) == {
        'kind': 'personal',
        'enterprise_id': None,
    }
    assert await service.get_active_workspace(db_session, user_id=13) == {
        'kind': 'personal',
        'enterprise_id': None,
    }
    enterprise_row = (
        await db_session.execute(sa.select(EnterpriseStub).where(EnterpriseStub.id == enterprise['id']))
    ).scalar_one()
    assert enterprise_row.status == 'deleted'
    assert (
        'on_enterprise_disbanded',
        {'enterprise_id': enterprise['id'], 'member_user_ids': [11, 12, 13]},
    ) in bus.events


@pytest.mark.asyncio
async def test_enterprise_workbench_app_enable_disable_uses_current_workspace_and_hooks(
    db_session: AsyncSession,
) -> None:
    workbench_bus = CapturingBus()
    service = _service(workbench_bus=workbench_bus)
    enterprise = await service.create_enterprise(db_session, user_id=21, name='Acme', slug='acme-hooks')
    await service.switch_active_workspace(
        db_session,
        user_id=21,
        kind='enterprise',
        enterprise_id=enterprise['id'],
    )
    disabled = await service.disable_current_workspace_app(db_session, user_id=21, app_id='knowledge')
    enabled = await service.enable_current_workspace_app(db_session, user_id=21, app_id='knowledge')

    assert disabled['status'] == 'disabled'
    assert enabled['status'] == 'active'
    assert workbench_bus.events == [
        (
            'on_app_disabled',
            {'workspace_kind': 'enterprise', 'user_id': None, 'enterprise_id': enterprise['id'], 'app_id': 'knowledge'},
        ),
        (
            'on_app_enabled',
            {'workspace_kind': 'enterprise', 'user_id': None, 'enterprise_id': enterprise['id'], 'app_id': 'knowledge'},
        ),
    ]


@pytest.mark.asyncio
async def test_workbench_rejects_unknown_apps_and_protects_auto_installed_personal_apps(
    db_session: AsyncSession,
) -> None:
    service = _service()
    await service.ensure_auto_apps(
        db_session,
        workspace_kind='personal',
        user_id=21,
        enterprise_id=None,
        enabled_by=21,
    )

    with pytest.raises(errors.NotFoundError):
        await service.enable_current_workspace_app(db_session, user_id=21, app_id='missing-app')
    with pytest.raises(errors.RequestError, match='auto_installed_personal_app_cannot_be_disabled'):
        await service.disable_current_workspace_app(db_session, user_id=21, app_id='knowledge')


@pytest.mark.asyncio
async def test_current_knowledge_credentials_follow_active_workspace(db_session: AsyncSession) -> None:
    service = _service()
    enterprise = await service.create_enterprise(db_session, user_id=31, name='Acme', slug='acme')

    public_instance = RagflowInstanceStub(
        scope='public',
        enterprise_id=None,
        url='https://knowledge.example',
        admin_api_key_encrypted=b'admin-public',
        public_pem='pem',
        status='active',
    )
    enterprise_instance = RagflowInstanceStub(
        scope='enterprise',
        enterprise_id=enterprise['id'],
        url='https://enterprise.example',
        admin_api_key_encrypted=b'admin-enterprise',
        public_pem='pem',
        status='active',
    )
    db_session.add_all([public_instance, enterprise_instance])
    await db_session.flush()
    db_session.add_all([
        RagflowCredentialStub(
            user_id=32,
            instance_id=public_instance.id,
            ragflow_user_id='u-public',
            ragflow_tenant_id='t-public',
            api_key_encrypted=b'key-public',
            status='active',
        ),
        RagflowCredentialStub(
            user_id=32,
            instance_id=enterprise_instance.id,
            ragflow_user_id='u-enterprise',
            ragflow_tenant_id='t-enterprise',
            api_key_encrypted=b'key-enterprise',
            status='active',
        ),
    ])
    await db_session.flush()

    personal = await service.get_current_knowledge_credentials(db_session, user_id=32)
    await service.apply_enterprise(
        db_session, enterprise_id=enterprise['id'], user_id=32, apply_message=None, invite_code=None
    )
    await service.approve_application(db_session, enterprise_id=enterprise['id'], app_id=2, decided_by=31)
    await service.switch_active_workspace(db_session, user_id=32, kind='enterprise', enterprise_id=enterprise['id'])
    enterprise_credentials = await service.get_current_knowledge_credentials(db_session, user_id=32)

    assert personal['workspace'] == {'kind': 'personal', 'enterprise_id': None}
    assert personal['credential']['ragflow_user_id'] == 'u-public'
    assert enterprise_credentials['workspace'] == {'kind': 'enterprise', 'enterprise_id': enterprise['id']}
    assert enterprise_credentials['credential']['ragflow_user_id'] == 'u-enterprise'


@pytest.mark.asyncio
async def test_refresh_current_knowledge_credentials_triggers_provision_for_active_instance(
    db_session: AsyncSession,
    monkeypatch,
) -> None:
    import backend.app.hasn.service.workbench_domain_service as service_mod

    service = _service()
    provisioner = CapturingProvisioningService()
    monkeypatch.setattr(service_mod, 'ragflow_provisioning_service', provisioner, raising=False)
    public_instance = RagflowInstanceStub(
        scope='public',
        enterprise_id=None,
        url='https://knowledge.example',
        admin_api_key_encrypted=b'admin-public',
        public_pem='pem',
        status='active',
    )
    db_session.add(public_instance)
    await db_session.flush()

    refreshed = await service.refresh_current_knowledge_credentials(db_session, user_id=32)

    assert provisioner.provisioned == [(32, public_instance.id)]
    assert refreshed['workspace'] == {'kind': 'personal', 'enterprise_id': None}
    assert refreshed['status'] == 'pending'
    assert refreshed['credential'] is None


@pytest.mark.asyncio
async def test_enterprise_ragflow_instance_config_upserts_and_disables(db_session: AsyncSession) -> None:
    service = _service()
    enterprise = await service.create_enterprise(db_session, user_id=41, name='Acme', slug='acme')

    saved = await service.save_enterprise_ragflow_instance(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=41,
        url='https://knowledge.example',
        admin_api_key='secret',
        public_pem='pem',
        default_embd_id='bge-m3',
        default_llm_id='qwen',
    )
    fetched = await service.get_enterprise_ragflow_instance(db_session, enterprise_id=enterprise['id'], user_id=41)
    disabled = await service.disable_enterprise_ragflow_instance(db_session, enterprise_id=enterprise['id'], user_id=41)

    assert saved['status'] == 'active'
    assert saved['admin_api_key_encrypted'] == 'stored'
    assert fetched['url'] == 'https://knowledge.example'
    assert disabled['status'] == 'disabled'


@pytest.mark.asyncio
async def test_enterprise_ragflow_instance_requires_owner_or_approved_admin(db_session: AsyncSession) -> None:
    service = _service()
    enterprise = await service.create_enterprise(db_session, user_id=51, name='Acme', slug='acme')
    db_session.add_all([
        MembershipStub(enterprise_id=enterprise['id'], user_id=52, role='admin', status='approved'),
        MembershipStub(enterprise_id=enterprise['id'], user_id=53, role='member', status='approved'),
        MembershipStub(enterprise_id=enterprise['id'], user_id=54, role='admin', status='pending'),
    ])
    await db_session.flush()

    await service.save_enterprise_ragflow_instance(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=51,
        url='https://knowledge.example',
        admin_api_key='owner-secret',
        public_pem='pem',
    )

    owner_fetched = await service.get_enterprise_ragflow_instance(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=51,
    )
    admin_tested = await service.test_enterprise_ragflow_instance(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=52,
    )
    admin_saved = await service.save_enterprise_ragflow_instance(
        db_session,
        enterprise_id=enterprise['id'],
        user_id=52,
        url='https://knowledge-admin.example',
        admin_api_key='admin-secret',
        public_pem='admin-pem',
    )

    assert owner_fetched['url'] == 'https://knowledge.example'
    assert admin_tested == {'enterprise_id': enterprise['id'], 'ok': True}
    assert admin_saved['url'] == 'https://knowledge-admin.example'

    for user_id in (53, 54, 55):
        with pytest.raises(errors.ForbiddenError):
            await service.get_enterprise_ragflow_instance(db_session, enterprise_id=enterprise['id'], user_id=user_id)
        with pytest.raises(errors.ForbiddenError):
            await service.save_enterprise_ragflow_instance(
                db_session,
                enterprise_id=enterprise['id'],
                user_id=user_id,
                url='https://blocked.example',
                admin_api_key='blocked',
                public_pem='blocked',
            )
        with pytest.raises(errors.ForbiddenError):
            await service.test_enterprise_ragflow_instance(db_session, enterprise_id=enterprise['id'], user_id=user_id)
        with pytest.raises(errors.ForbiddenError):
            await service.disable_enterprise_ragflow_instance(
                db_session,
                enterprise_id=enterprise['id'],
                user_id=user_id,
            )


@pytest.mark.asyncio
async def test_current_knowledge_datasets_are_loaded_from_active_ragflow_instance(
    db_session: AsyncSession,
) -> None:
    calls: list[tuple[str, str, dict]] = []
    service = _ragflow_service(calls)
    await _seed_active_ragflow_workspace(db_session)

    result = await service.list_current_knowledge_datasets(db_session, user_id=12, limit=50, offset=0)

    assert result['items'][0]['id'] == 'ds-1'
    assert result['items'][0]['documents'][0]['doc_id'] == 'doc-1'
    assert calls == [
        (
            'GET',
            '/api/v1/datasets',
            {
                'params': {'page': 1, 'page_size': 50, 'orderby': 'create_time', 'desc': True},
                'headers': {'Authorization': 'Bearer ragflow-user-token'},
            },
        ),
        (
            'GET',
            '/api/v1/datasets/ds-1/documents',
            {
                'params': {'page': 1, 'page_size': 50, 'orderby': 'create_time', 'desc': True},
                'headers': {'Authorization': 'Bearer ragflow-user-token'},
            },
        ),
    ]


@pytest.mark.asyncio
async def test_current_knowledge_search_and_upload_proxy_ragflow_with_user_token(
    db_session: AsyncSession,
) -> None:
    calls: list[tuple[str, str, dict]] = []
    service = _ragflow_service(calls)
    await _seed_active_ragflow_workspace(db_session)

    search = await service.search_current_knowledge(db_session, user_id=12, query='enterprise credentials', limit=5)
    upload = await service.upload_current_knowledge_document(
        db_session,
        user_id=12,
        title='Runbook.txt',
        content_text='rotate enterprise credentials safely',
        metadata={'dataset_id': 'ds-1'},
    )

    assert search['items'][0]['doc_id'] == 'doc-1'
    assert search['items'][0]['content_text'] == 'rotate enterprise credentials safely'
    assert upload['doc_id'] == 'doc-new'
    assert calls == [
        (
            'GET',
            '/api/v1/datasets',
            {
                'params': {'page': 1, 'page_size': 30, 'orderby': 'create_time', 'desc': True},
                'headers': {'Authorization': 'Bearer ragflow-user-token'},
            },
        ),
        (
            'POST',
            '/api/v1/datasets/ds-1/search',
            {
                'json': {'question': 'enterprise credentials', 'top_k': 5, 'page': 1, 'size': 5},
                'headers': {'Authorization': 'Bearer ragflow-user-token'},
            },
        ),
        (
            'POST',
            '/api/v1/datasets/ds-1/documents?type=empty',
            {
                'json': {'name': 'Runbook.txt'},
                'headers': {'Authorization': 'Bearer ragflow-user-token'},
            },
        ),
        (
            'POST',
            '/api/v1/datasets/ds-1/documents/doc-new/chunks',
            {
                'json': {'content': 'rotate enterprise credentials safely'},
                'headers': {'Authorization': 'Bearer ragflow-user-token'},
            },
        ),
    ]


@pytest.mark.asyncio
async def test_current_knowledge_proxy_blocks_without_active_credential(
    db_session: AsyncSession,
) -> None:
    service = _ragflow_service([])
    db_session.add(RagflowInstanceStub(scope='public', url='https://knowledge.example', status='active'))
    await db_session.flush()

    with pytest.raises(errors.RequestError, match='knowledge_credentials_not_active'):
        await service.search_current_knowledge(db_session, user_id=99, query='missing', limit=5)


@pytest.mark.asyncio
async def test_current_knowledge_search_refreshes_credentials_once_after_ragflow_401(
    db_session: AsyncSession,
    monkeypatch,
) -> None:
    import backend.app.hasn.service.workbench_domain_service as service_mod

    service = _ragflow_service([])
    _, instance_id = await _seed_active_ragflow_workspace(db_session)
    client = ExpiringRAGFlowClient()
    service.ragflow_client_factory = lambda _base_url: client
    provisioner = RefreshingProvisioningService(db_session)
    monkeypatch.setattr(service_mod, 'ragflow_provisioning_service', provisioner, raising=False)

    result = await service.search_current_knowledge(
        db_session,
        user_id=12,
        query='enterprise credentials',
        limit=5,
        dataset_id='ds-1',
    )

    assert result['items'][0]['content_text'] == 'fresh token search result'
    assert provisioner.provisioned == [(12, instance_id)]
    assert [call['headers'] for call in client.calls] == [
        {'Authorization': 'Bearer ragflow-user-token'},
        {'Authorization': 'Bearer fresh-token'},
    ]


def service_mod_timezone_now_minus_one_day():
    from backend.utils.timezone import timezone

    return timezone.now() - timedelta(days=1)
