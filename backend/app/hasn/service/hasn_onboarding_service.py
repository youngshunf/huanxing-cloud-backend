"""S2 HASN onboarding service.

Scope guard:
- Implements only phone auth adaptation and onboarding ensure.
- Does not implement message hub, runtime scheduling, sandbox creation, or channel bridge.
- Persists/updates only server-authoritative identity, node, binding, default-agent,
  and pending-intent association data; runtime-private endpoint/workspace/PID/CLI/OAuth
  details are intentionally filtered out.
"""
from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Protocol

import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.model import User
from backend.app.hasn.schema.hasn_onboarding import (
    AgentSummary,
    HumanSummary,
    OnboardingEnsureRequest,
    OnboardingEnsureResponse,
    OwnerBindingSummary,
    PhoneSendCodeRequest,
    PhoneSendCodeResponse,
    PhoneVerifyRequest,
    PhoneVerifyResponse,
    SandboxSummary,
)
from backend.app.hasn.service import hasn_auth as hasn_auth_service
from backend.app.hasn.service.hasn_node_bindings_service import hasn_node_bindings_service
from backend.common.exception import errors
from backend.common.security.jwt import create_access_token
from backend.common.sms import sms_service
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.timezone import timezone

SMS_CODE_PREFIX = 'sms_code'
SMS_CODE_EXPIRE = 1800
SMS_RATE_PREFIX = 'sms_rate'
SMS_RATE_EXPIRE = 60

DEFAULT_AGENT_NAME = 'assistant'
DEFAULT_AGENT_DISPLAY_NAME = '唤星默认 Agent'
DEFAULT_AGENT_DESCRIPTION = 'HASN onboarding 默认 Agent，用于承接首次登录后的基础会话与 pending intent。'
DEFAULT_AGENT_TEMPLATE: dict[str, Any] = {
    'template_id': 'hasn_default_agent_v1',
    'protocol': 'hasn/0.2',
    'role': 'owner_default_agent',
    'capabilities': [
        'owner_visible_inbox',
        'pending_intent_resume',
        'runtime_optional',
    ],
    'runtime_required': False,
}

PRIVATE_NODE_INFO_KEYS = {
    'workspace',
    'workspace_path',
    'endpoint',
    'local_endpoint',
    'pid',
    'process_id',
    'cli_args',
    'oauth_path',
    'session_cache',
}


class RedisLike(Protocol):
    async def exists(self, key: str) -> bool: ...
    async def ttl(self, key: str) -> int: ...
    async def setex(self, key: str, seconds: int, value: str) -> Any: ...
    async def get(self, key: str) -> Any: ...
    async def delete(self, key: str) -> Any: ...


class SmsLike(Protocol):
    async def send_code(self, phone: str, code: str) -> bool: ...


class PlatformUserGateway(Protocol):
    async def get_or_create_phone_user(self, db: AsyncSession, phone: str) -> tuple[Any, bool]: ...


class OnboardingGateway(Protocol):
    async def get_user(self, db: AsyncSession, user_id: int) -> Any | None: ...
    async def ensure_human(self, db: AsyncSession, user: Any) -> tuple[Any, bool]: ...
    async def ensure_node(
        self, db: AsyncSession, user_id: int, owner_id: str, request: OnboardingEnsureRequest
    ) -> Any: ...
    async def ensure_owner_binding(self, db: AsyncSession, node_id: str, owner_id: str) -> Any: ...
    async def ensure_default_agent(self, db: AsyncSession, owner_id: str, node_id: str | None) -> tuple[Any, bool]: ...
    async def consume_pending_intent(
        self, db: AsyncSession, pending_intent_id: str, owner_id: str, agent_hasn_id: str
    ) -> bool: ...
    async def get_sandbox_summary(self, db: AsyncSession, owner_id: str) -> SandboxSummary | None: ...


class SqlAlchemyPlatformUserGateway:
    """Platform-user adapter for HASN phone verification."""

    async def get_or_create_phone_user(self, db: AsyncSession, phone: str) -> tuple[User, bool]:
        user = await user_dao.select_model_by_column(db, phone=phone)
        if user:
            return user, False

        username = phone
        nickname = f'{phone[:3]}****{phone[-4:]}'
        if await user_dao.get_by_username(db, username):
            username = f'{phone}_{_generate_code(4)}'

        user = User(
            username=username,
            nickname=nickname,
            phone=phone,
            password=None,
            salt=None,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user, True


class SqlAlchemyOnboardingGateway:
    """Production persistence adapter for S2 onboarding business operations."""

    async def get_user(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(sa.select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def ensure_human(self, db: AsyncSession, user: User) -> tuple[Any, bool]:
        result = await hasn_auth_service.register_hasn_identity(
            db=db,
            user_id=user.id,
            name=user.nickname or user.username or '唤星用户',
            avatar=user.avatar,
            bio=user.bio,
        )
        return result['human'], not result.get('already_exists', False)

    async def ensure_node(self, db: AsyncSession, user_id: int, owner_id: str, request: OnboardingEnsureRequest) -> Any:
        node_info = _safe_node_info(request)
        node = await hasn_auth_service.register_node(
            db=db,
            node_id=request.node.node_id,
            user_id=user_id,
            owner_hasn_id=owner_id,
            node_type=_coerce_node_type(request.node.platform),
            node_name=request.node.device_name,
            node_info=node_info,
        )
        return node

    async def ensure_owner_binding(self, db: AsyncSession, node_id: str, owner_id: str) -> Any:
        return await hasn_node_bindings_service.add_owner_binding(
            db=db,
            node_id=node_id,
            owner_id=owner_id,
            auth_profile='bearer_token',
            scopes={'bind_owner': True, 'register_agent': True, 'onboarding': True},
            expires_at=timezone.now() + timedelta(days=7),
        )

    async def ensure_default_agent(self, db: AsyncSession, owner_id: str, node_id: str | None) -> tuple[Any, bool]:
        result = await hasn_auth_service.register_hasn_agent(
            db=db,
            owner_hasn_id=owner_id,
            agent_name=DEFAULT_AGENT_NAME,
            display_name=DEFAULT_AGENT_DISPLAY_NAME,
            agent_type='cloud',
            node_id=node_id,
            role='primary',
            description=DEFAULT_AGENT_DESCRIPTION,
            capabilities=[DEFAULT_AGENT_TEMPLATE],
            created_via='onboarding',
        )
        return result['agent'], not result.get('already_exists', False)

    async def consume_pending_intent(
        self, db: AsyncSession, pending_intent_id: str, owner_id: str, agent_hasn_id: str
    ) -> bool:
        """Associate a pending intent with onboarding result.

        This is specific S2 business logic, not a generic CRUD surface. The table
        is a S1 codegen input; S5 will own full channel/pending-intent management.
        """
        result = await db.execute(
            sa.text(
                '''
                UPDATE public.hasn_pending_intents
                SET owner_id = :owner_id,
                    agent_hasn_id = :agent_hasn_id,
                    status = 'consumed',
                    consumed_at = now(),
                    updated_time = now()
                WHERE intent_id = :intent_id
                  AND status = 'pending'
                  AND expires_at > now()
                RETURNING intent_id
                '''
            ),
            {
                'owner_id': owner_id,
                'agent_hasn_id': agent_hasn_id,
                'intent_id': pending_intent_id,
            },
        )
        return result.first() is not None

    async def get_sandbox_summary(self, db: AsyncSession, owner_id: str) -> SandboxSummary | None:
        """Return existing S3 sandbox route if present; never creates a sandbox in S2."""
        try:
            result = await db.execute(
                sa.text(
                    '''
                    SELECT sandbox_id, state, router_base_url
                    FROM public.hasn_tenant_sandboxes
                    WHERE owner_id = :owner_id
                      AND state <> 'deleted'
                    ORDER BY updated_time DESC NULLS LAST, created_time DESC
                    LIMIT 1
                    '''
                ),
                {'owner_id': owner_id},
            )
            row = result.mappings().first()
        except Exception:
            return None

        if not row:
            return None
        return SandboxSummary(
            sandbox_id=row['sandbox_id'],
            status=_sandbox_status(row['state']),
            base_url=row['router_base_url'],
        )


@dataclass(slots=True)
class HasnPhoneAuthService:
    redis: RedisLike = field(default=redis_client)
    sms: SmsLike = field(default=sms_service)
    users: PlatformUserGateway = field(default_factory=SqlAlchemyPlatformUserGateway)
    token_expire_seconds: int = settings.TOKEN_EXPIRE_SECONDS
    code_generator: Any | None = None
    token_creator: Any = create_access_token

    async def send_code(self, request: PhoneSendCodeRequest) -> PhoneSendCodeResponse:
        phone = request.phone
        rate_key = f'{SMS_RATE_PREFIX}:{phone}'
        if await self.redis.exists(rate_key):
            ttl = await self.redis.ttl(rate_key)
            return PhoneSendCodeResponse(ok=False, retry_after_sec=max(int(ttl or 0), 0))

        generator = self.code_generator or _generate_code
        code = generator()
        await self.redis.setex(f'{SMS_CODE_PREFIX}:{phone}', SMS_CODE_EXPIRE, code)

        if settings.ENVIRONMENT == 'dev':
            print(f'[HASN] phone verification code [{phone}]: {code}')

        sent = await self.sms.send_code(phone, code)
        if not sent and settings.ENVIRONMENT != 'dev':
            raise errors.RequestError(msg='验证码发送失败，请稍后重试')

        await self.redis.setex(rate_key, SMS_RATE_EXPIRE, '1')
        return PhoneSendCodeResponse(ok=True, retry_after_sec=0)

    async def verify(self, db: AsyncSession, request: PhoneVerifyRequest) -> PhoneVerifyResponse:
        phone = request.phone
        stored_code = await self.redis.get(f'{SMS_CODE_PREFIX}:{phone}')
        stored_code = _decode_redis_value(stored_code)
        if not stored_code:
            raise errors.RequestError(msg='验证码已过期，请重新获取')
        if stored_code != request.code:
            raise errors.RequestError(msg='验证码错误')

        await self.redis.delete(f'{SMS_CODE_PREFIX}:{phone}')
        user, _ = await self.users.get_or_create_phone_user(db, phone)
        user.last_login_time = timezone.now()
        await db.flush()

        access_token = await self.token_creator(
            user.id,
            multi_login=user.is_multi_login,
            username=user.username,
            nickname=user.nickname,
            phone=user.phone,
            pending_intent_id=request.pending_intent_id,
            hasn_onboarding=True,
        )

        # PR7: ensure newapi user + token so the daemon receives per-owner
        # LLM credentials with the login response. This mirrors the admin
        # `/auth/phone-login` flow so the hasn daemon path is functionally
        # equivalent — one set of LLM credentials per owner, shared by all
        # of that owner's agents via per-profile `.env` files.
        from backend.app.llm.service.llm_newapi_user_mapping_service import (
            llm_newapi_user_mapping_service,
        )
        from backend.core.conf import settings

        llm_token: str | None = None
        llm_base_url: str | None = settings.LLM_API_BASE_URL
        try:
            mapping = await llm_newapi_user_mapping_service.ensure_newapi_user(
                db,
                user.id,
                username=user.phone or user.username,
                nickname=user.nickname or '',
            )
            llm_token = f'sk-{mapping.newapi_token_key}'
        except Exception as exc:  # noqa: BLE001 — surface real failure, no fake fallback
            raise errors.ServerError(msg=f'LLM 服务初始化失败: {exc}') from exc

        return PhoneVerifyResponse(
            access_token=access_token.access_token,
            expires_in_sec=self.token_expire_seconds,
            llm_token=llm_token,
            llm_base_url=llm_base_url,
            # 默认从全局 settings 拉；后续支持 user 表 llm_model 列时
            # 改成 `getattr(user, 'llm_model', None) or settings.LLM_DEFAULT_MODEL`
            llm_model=settings.LLM_DEFAULT_MODEL,
        )


@dataclass(slots=True)
class HasnOnboardingService:
    gateway: OnboardingGateway = field(default_factory=SqlAlchemyOnboardingGateway)

    async def ensure(
        self, db: AsyncSession, user_id: int, request: OnboardingEnsureRequest
    ) -> OnboardingEnsureResponse:
        user = await self.gateway.get_user(db, user_id)
        if user is None:
            raise errors.NotFoundError(msg='用户不存在')

        human, _ = await self.gateway.ensure_human(db, user)
        node = await self.gateway.ensure_node(db, user_id, human.hasn_id, request)
        binding = await self.gateway.ensure_owner_binding(db, node.node_id, human.hasn_id)
        agent, _ = await self.gateway.ensure_default_agent(db, human.hasn_id, node.node_id)

        if request.pending_intent_id:
            await self.gateway.consume_pending_intent(
                db,
                pending_intent_id=request.pending_intent_id,
                owner_id=human.hasn_id,
                agent_hasn_id=agent.hasn_id,
            )

        # 签发 Agent JWT
        from backend.common.security.agent_jwt import create_agent_access_token, get_agent_scopes_cached
        scopes_config = await get_agent_scopes_cached(agent.hasn_id, db)
        agent_token = await create_agent_access_token(
            agent_hasn_id=agent.hasn_id,
            agent_name=getattr(agent, 'name', None) or DEFAULT_AGENT_DISPLAY_NAME,
            owner_hasn_id=human.hasn_id,
            owner_user_id=user_id,
            scopes=scopes_config['scopes'],
        )

        sandbox = await self.gateway.get_sandbox_summary(db, human.hasn_id)
        return OnboardingEnsureResponse(
            human=HumanSummary(
                human_id=human.hasn_id,
                owner_id=human.hasn_id,
                display_name=getattr(human, 'name', None),
            ),
            owner_binding=OwnerBindingSummary(
                owner_id=human.hasn_id,
                node_id=node.node_id,
                status=_binding_status(getattr(binding, 'status', 'active')),
                revision=int(getattr(binding, 'sync_revision', 1) or 1),
            ),
            default_agent=AgentSummary(
                agent_id=agent.hasn_id,
                owner_id=human.hasn_id,
                hasn_id=agent.hasn_id,
                # PR1.5: 透传 hasn_agents.star_id 给 daemon，避免 daemon 用
                # hasn_id 顶替 star_id 写本地导致绑定时报 empty。
                star_id=getattr(agent, 'star_id', '') or '',
                display_name=getattr(agent, 'name', None),
                access_token=agent_token.access_token,
                scopes=agent_token.scopes,
                expire_time=agent_token.access_token_expire_time.isoformat(),
            ),
            sandbox=sandbox,
            sync_cursor=f'owner:{human.hasn_id}:0',
        )


def _generate_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def _decode_redis_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode()
    return str(value)


def _coerce_node_type(platform: str) -> str:
    normalized = (platform or '').lower()
    if normalized in {'ios', 'android'}:
        return 'mobile'
    if normalized in {'web', 'browser'}:
        return 'web'
    if normalized in {'sdk', 'server'}:
        return 'sdk'
    return 'desktop'


def _safe_node_info(request: OnboardingEnsureRequest) -> dict[str, Any]:
    raw = {
        'device_fingerprint': request.node.node_id,
        'device_platform': request.node.platform,
        'client_version': request.node.client_version,
        'protocol': request.client.protocol,
        'supported_extensions': request.client.supported_extensions or [],
    }
    return {key: value for key, value in raw.items() if key not in PRIVATE_NODE_INFO_KEYS and value is not None}


def _binding_status(status: str) -> str:
    if status == 'revoked':
        return 'revoked'
    if status == 'expired':
        return 'expiring'
    return 'active'


def _sandbox_status(state: str) -> str:
    if state == 'error':
        return 'failed'
    if state in {'creating', 'active', 'sleeping', 'deleted', 'failed'}:
        return state
    return 'sleeping'


hasn_phone_auth_service = HasnPhoneAuthService()
hasn_onboarding_service = HasnOnboardingService()
