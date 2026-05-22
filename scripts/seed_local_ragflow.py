"""
Seed 本地 RAGFlow 实例到数据库

从 .env 配置文件读取公共 RAGFlow 实例配置，并写入数据库
用于本地开发测试和生产环境部署
"""

import asyncio
from datetime import datetime, timezone

import sqlalchemy as sa

from backend.app.hasn.model import HasnRagflowInstance
from backend.app.hasn.util.secret_crypto import encrypt_ragflow_secret
from backend.core.conf import settings
from backend.database.db import async_db_session


async def seed_public_ragflow():
    """从配置文件 Seed 公共 RAGFlow 实例"""

    # 从配置文件读取
    url = settings.RAGFLOW_PUBLIC_URL
    admin_api_key = settings.RAGFLOW_PUBLIC_ADMIN_API_KEY
    default_embd_id = settings.RAGFLOW_DEFAULT_EMBD_ID
    default_llm_id = settings.RAGFLOW_DEFAULT_LLM_ID

    if not url or not admin_api_key:
        print("⚠️  未配置 RAGFlow 公共实例（RAGFLOW_PUBLIC_URL 或 RAGFLOW_PUBLIC_ADMIN_API_KEY 为空）")
        print("   请在 .env 中配置后重试")
        return None

    async with async_db_session() as db:
        # 检查是否已存在相同 URL 的实例
        existing = (await db.execute(
            sa.select(HasnRagflowInstance)
            .where(HasnRagflowInstance.url == url)
        )).scalar_one_or_none()

        if existing:
            print(f"✓ RAGFlow 公共实例已存在 (ID: {existing.id})")
            print(f"  URL: {url}")
            print(f"  Status: {existing.status}")
            return existing.id

        # 加密管理员 API Key
        encrypted_key = encrypt_ragflow_secret(admin_api_key)

        # 创建新实例
        now = datetime.now(timezone.utc)
        instance = HasnRagflowInstance(
            scope='public',
            enterprise_id=None,
            url=url,
            admin_api_key_encrypted=encrypted_key,
            public_pem=None,
            default_embd_id=default_embd_id,
            default_llm_id=default_llm_id,
            status='active',
            created_at=now,
            updated_at=now,
        )

        db.add(instance)
        await db.commit()
        await db.refresh(instance)

        print(f"✓ 成功创建 RAGFlow 公共实例 (ID: {instance.id})")
        print(f"  URL: {url}")
        print(f"  Scope: public")
        print(f"  Status: active")
        print(f"  Default Embedding: {default_embd_id}")
        print(f"  Default LLM: {default_llm_id}")

        return instance.id


if __name__ == '__main__':
    asyncio.run(seed_public_ragflow())
