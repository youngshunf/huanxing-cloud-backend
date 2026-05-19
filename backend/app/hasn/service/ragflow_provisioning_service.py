from __future__ import annotations

import secrets

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

import httpx
import sqlalchemy as sa

from backend.app.admin.model.user import User
from backend.app.hasn.model import HasnRagflowCredential, HasnRagflowInstance
from backend.app.hasn.service.ragflow_client import RAGFlowClient
from backend.app.hasn.util.rsa_pwd import rsa_encrypt_password
from backend.app.hasn.util.secret_crypto import decrypt_ragflow_secret, encrypt_ragflow_secret
from backend.database.db import async_db_session
from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker


class CredentialRepository(Protocol):
    async def get_instance(self, instance_id: int) -> None: ...
    async def get_user(self, user_id: int) -> None: ...
    async def upsert_pending_credential(self, *, user_id: int, instance_id: int, reason: str) -> None: ...
    async def upsert_active_credential(
        self,
        *,
        user_id: int,
        instance_id: int,
        ragflow_user_id: str,
        ragflow_tenant_id: str,
        api_key: str,
    ) -> None: ...
    async def mark_revoked(self, credential_id: int) -> None: ...
    async def get_credential(self, credential_id: int) -> None: ...


@dataclass(frozen=True)
class RAGFlowCredentialForRevoke:
    id: int
    user_id: int
    instance_id: int
    ragflow_user_id: str
    ragflow_tenant_id: str
    api_key: str
    status: str
    instance: HasnRagflowInstance


@dataclass(frozen=True)
class ProvisionedCredential:
    user_id: int
    instance_id: int
    ragflow_user_id: str
    ragflow_tenant_id: str
    status: str


class SqlAlchemyRAGFlowCredentialRepository:
    def __init__(self, session_factory: async_sessionmaker | None = None) -> None:
        self.session_factory = session_factory or async_db_session

    async def get_instance(self, instance_id: int):
        async with self.session_factory() as db:
            instance = (
                await db.execute(sa.select(HasnRagflowInstance).where(HasnRagflowInstance.id == instance_id))
            ).scalar_one_or_none()
            if instance is None:
                raise RuntimeError(f'RAGFlow instance {instance_id} not found')
            return instance

    async def get_user(self, user_id: int):
        async with self.session_factory() as db:
            user = (await db.execute(sa.select(User).where(User.id == user_id))).scalar_one_or_none()
            if user is None:
                raise RuntimeError(f'user {user_id} not found')
            return user

    async def upsert_pending_credential(self, *, user_id: int, instance_id: int, reason: str):
        async with self.session_factory.begin() as db:
            credential = await self._find_credential(db, user_id=user_id, instance_id=instance_id)
            if credential is None:
                credential = HasnRagflowCredential(
                    user_id=user_id,
                    instance_id=instance_id,
                    ragflow_user_id='',
                    ragflow_tenant_id='',
                    api_key_encrypted=b'',
                    status='pending',
                    last_error=reason,
                )
                db.add(credential)
            elif credential.status != 'active':
                credential.status = 'pending'
                credential.last_error = reason
                self._touch(credential)
            await db.flush()
            return credential

    async def upsert_active_credential(
        self,
        *,
        user_id: int,
        instance_id: int,
        ragflow_user_id: str,
        ragflow_tenant_id: str,
        api_key: str,
    ):
        async with self.session_factory.begin() as db:
            credential = await self._find_credential(db, user_id=user_id, instance_id=instance_id)
            if credential is None:
                credential = HasnRagflowCredential(
                    user_id=user_id,
                    instance_id=instance_id,
                    ragflow_user_id=ragflow_user_id,
                    ragflow_tenant_id=ragflow_tenant_id,
                    api_key_encrypted=encrypt_ragflow_secret(api_key),
                    status='active',
                    last_error=None,
                )
                db.add(credential)
            else:
                credential.ragflow_user_id = ragflow_user_id
                credential.ragflow_tenant_id = ragflow_tenant_id
                credential.api_key_encrypted = encrypt_ragflow_secret(api_key)
                credential.status = 'active'
                credential.last_error = None
                self._touch(credential)
            await db.flush()
            return ProvisionedCredential(
                user_id=user_id,
                instance_id=instance_id,
                ragflow_user_id=ragflow_user_id,
                ragflow_tenant_id=ragflow_tenant_id,
                status='active',
            )

    async def mark_revoked(self, credential_id: int) -> None:
        async with self.session_factory.begin() as db:
            credential = (
                await db.execute(sa.select(HasnRagflowCredential).where(HasnRagflowCredential.id == credential_id))
            ).scalar_one_or_none()
            if credential is None:
                return
            credential.status = 'revoked'
            credential.last_error = None
            self._touch(credential)

    async def get_credential(self, credential_id: int):
        async with self.session_factory() as db:
            credential = (
                await db.execute(sa.select(HasnRagflowCredential).where(HasnRagflowCredential.id == credential_id))
            ).scalar_one_or_none()
            if credential is None:
                raise RuntimeError(f'RAGFlow credential {credential_id} not found')
            instance = (
                await db.execute(sa.select(HasnRagflowInstance).where(HasnRagflowInstance.id == credential.instance_id))
            ).scalar_one_or_none()
            if instance is None:
                raise RuntimeError(f'RAGFlow instance {credential.instance_id} not found')
            return RAGFlowCredentialForRevoke(
                id=credential.id,
                user_id=credential.user_id,
                instance_id=credential.instance_id,
                ragflow_user_id=credential.ragflow_user_id,
                ragflow_tenant_id=credential.ragflow_tenant_id,
                api_key=decrypt_ragflow_secret(credential.api_key_encrypted),
                status=credential.status,
                instance=instance,
            )

    @staticmethod
    async def _find_credential(db, *, user_id: int, instance_id: int):
        return (
            await db.execute(
                sa.select(HasnRagflowCredential).where(
                    HasnRagflowCredential.user_id == user_id,
                    HasnRagflowCredential.instance_id == instance_id,
                )
            )
        ).scalar_one_or_none()

    @staticmethod
    def _touch(credential) -> None:
        if hasattr(credential, 'updated_at'):
            credential.updated_at = timezone.now()


class RAGFlowProvisioningService:
    def __init__(self, repository: CredentialRepository | None = None) -> None:
        self.repository = repository

    async def provision_one(self, user_id: int, instance_id: int):
        if self.repository is None:
            raise RuntimeError('credential repository is required for provision_one')
        instance = await self.repository.get_instance(instance_id)
        if instance.status != 'active':
            return await self.repository.upsert_pending_credential(
                user_id=user_id,
                instance_id=instance_id,
                reason='instance not yet configured',
            )

        user = await self.repository.get_user(user_id)
        client = RAGFlowClient(instance.url)
        password = secrets.token_urlsafe(32)
        encrypted_password = rsa_encrypt_password(password, instance.public_pem)
        response = await client.request(
            'POST',
            '/api/v1/users',
            json={
                'email': f'u-{user.id}@ragflow.internal',
                'password': encrypted_password,
                'nickname': getattr(user, 'nickname', None) or f'user-{user.id}',
            },
        )
        ragflow_user_id = response.body['data']['id']
        jwt = response.headers.get('Authorization') or response.headers.get('authorization')
        if not jwt:
            raise RuntimeError('RAGFlow registration response missing Authorization header')
        token = (await client.post('/api/v1/system/tokens', headers={'Authorization': jwt}))['data']['token']
        await client.patch(
            '/api/v1/users/me/models',
            json={
                'tenant_id': ragflow_user_id,
                'embd_id': instance.default_embd_id,
                'llm_id': instance.default_llm_id or '',
                'asr_id': '',
                'img2txt_id': '',
            },
            headers={'Authorization': f'Bearer {token}'},
        )
        await client.post(
            '/api/v1/datasets',
            json={'name': '我的知识库'},
            headers={'Authorization': f'Bearer {token}'},
        )
        return await self.repository.upsert_active_credential(
            user_id=user_id,
            instance_id=instance_id,
            ragflow_user_id=ragflow_user_id,
            ragflow_tenant_id=ragflow_user_id,
            api_key=token,
        )

    async def revoke_one(self, credential_id: int) -> None:
        if self.repository is None:
            raise RuntimeError('credential repository is required for revoke_one')
        credential = await self.repository.get_credential(credential_id)
        if credential.status == 'revoked' or not credential.api_key:
            await self.repository.mark_revoked(credential_id)
            return
        client = RAGFlowClient(credential.instance.url)
        try:
            await client.delete(
                f'/api/v1/system/tokens/{credential.api_key}',
                headers={'Authorization': f'Bearer {credential.api_key}'},
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (401, 404):
                raise
        await self.repository.mark_revoked(credential_id)


ragflow_provisioning_service = RAGFlowProvisioningService(SqlAlchemyRAGFlowCredentialRepository())
