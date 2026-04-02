import uuid
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.model.hasn_clients import HasnClients
from backend.app.hasn.schema.hasn_api_keys import CreateApiKeyRes
from backend.app.hasn.service.hasn_auth import _generate_api_key

class HasnApiKeyService:
    @staticmethod
    async def create_api_key(
        db: AsyncSession,
        user_hasn_id: str,
        name: str,
        client_type: str = 'api_key',
    ) -> CreateApiKeyRes:
        """创建新的 API Key"""
        client_id = f"n_{uuid.uuid4().hex[:12]}"
        api_key, api_key_hash = _generate_api_key()

        client = HasnClients(
            client_id=client_id,
            user_hasn_id=user_hasn_id,
            client_type=client_type,
            device_name=name,
            device_info={'generated_by': 'user_ui'},
            api_key_hash=api_key_hash,
            status='active',
            capacity=1,
        )
        db.add(client)
        await db.flush()

        return CreateApiKeyRes(
            client_id=client.client_id,
            device_name=client.device_name,
            created_time=client.created_time,
            last_seen_at=client.last_seen_at,
            api_key=api_key,
        )

    @staticmethod
    async def list_api_keys(
        db: AsyncSession,
        user_hasn_id: str,
    ) -> Sequence[HasnClients]:
        """列出用户的所有 API Key (包括 auto-login 产生的 desktop keys)"""
        result = await db.execute(
            select(HasnClients).where(
                HasnClients.user_hasn_id == user_hasn_id,
                HasnClients.status == 'active',
                HasnClients.api_key_hash.is_not(None),
            ).order_by(HasnClients.created_time.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def delete_api_key(
        db: AsyncSession,
        user_hasn_id: str,
        client_id: str,
    ) -> None:
        """删除(吊销) API Key"""
        result = await db.execute(
            select(HasnClients).where(
                HasnClients.client_id == client_id,
                HasnClients.user_hasn_id == user_hasn_id,
                HasnClients.status == 'active',
            )
        )
        client = result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="API Key 不存在")
        
        client.status = 'deleted'
        await db.flush()

hasn_api_key_service = HasnApiKeyService()
