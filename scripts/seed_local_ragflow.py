# -*- coding: utf-8 -*-
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
    public_key = settings.RAGFLOW_PUBLIC_RSA_PUBLIC_KEY
    default_embd_id = settings.RAGFLOW_DEFAULT_EMBD_ID
    default_llm_id = settings.RAGFLOW_DEFAULT_LLM_ID

    if not url:
        print("⚠️  未配置 RAGFlow 公共实例（RAGFLOW_PUBLIC_URL 为空）")
        print("   请在 .env 中配置后重试")
        return None

    if not public_key:
        print("⚠️  未配置 RAGFlow RSA 公钥（RAGFLOW_PUBLIC_RSA_PUBLIC_KEY 为空）")
        print("   注意：RAGFlow 注册需要 RSA 公钥来加密密码")
        print("   请从 RAGFlow 管理后台获取公钥并配置到 .env")
        # 继续创建记录，但 provision 会失败直到配置公钥

    async with async_db_session() as db:
        # 检查是否已存在相同 URL 的实例
        existing = (await db.execute(
            sa.select(HasnRagflowInstance)
            .where(HasnRagflowInstance.url == url)
        )).scalar_one_or_none()

        if existing:
            # 检查是否需要更新公钥
            needs_update = False
            if public_key and existing.public_pem != public_key:
                needs_update = True
                existing.public_pem = public_key
                await db.commit()
                await db.refresh(existing)

            print(f"✓ RAGFlow 公共实例已存在 (ID: {existing.id})")
            print(f"  URL: {url}")
            print(f"  Status: {existing.status}")
            print(f"  Public Key: {'已配置' if existing.public_pem else '未配置'}")
            if needs_update:
                print(f"  ✓ 已更新 RSA 公钥")
            return existing.id

        # 创建新实例（admin_api_key_encrypted 使用占位符，因为不需要管理员 key）
        placeholder_key = encrypt_ragflow_secret('not-used')

        # 创建新实例
        now = datetime.now(timezone.utc)
        instance = HasnRagflowInstance(
            scope='public',
            enterprise_id=None,
            url=url,
            admin_api_key_encrypted=placeholder_key,  # 占位符，实际不使用
            public_pem=public_key or None,  # RSA 公钥
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
        print(f"  Public Key: {'已配置' if public_key else '未配置（需要配置才能正常 provision）'}")

        return instance.id


if __name__ == '__main__':
    asyncio.run(seed_public_ragflow())
