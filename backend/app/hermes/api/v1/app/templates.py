"""Hermes 用户端 Agent 模板列表（M1 §5.4）。

GET /api/v1/hermes/app/templates
- JOIN marketplace_app (app_type='agent_template') + marketplace_app_version (is_latest=true)
- 返回过滤敏感字段：只暴露 {app_id, name, description, emoji, icon_url, version}
  package_url + file_hash 是 backend 内部用（apply_template 时推给 runtime），不返给浏览器
- marketplace 没有 publish 模板时返 []（不报错）
"""
from __future__ import annotations

import sqlalchemy as sa
from fastapi import APIRouter

from backend.app.marketplace.model.marketplace_app import MarketplaceApp
from backend.app.marketplace.model.marketplace_app_version import MarketplaceAppVersion
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('', summary='获取可选 Agent 模板列表', dependencies=[DependsJwtAuth])
async def list_agent_templates(db: CurrentSession) -> ResponseModel:
    stmt = (
        sa.select(
            MarketplaceApp.app_id,
            MarketplaceApp.name,
            MarketplaceApp.description,
            MarketplaceApp.emoji,
            MarketplaceApp.icon_url,
            MarketplaceAppVersion.version,
        )
        .join(
            MarketplaceAppVersion,
            MarketplaceAppVersion.app_id == MarketplaceApp.app_id,
        )
        .where(
            sa.text("marketplace_app.app_type = 'agent_template'"),
            MarketplaceAppVersion.is_latest.is_(True),
        )
        .order_by(MarketplaceApp.id.asc())
    )
    rows = (await db.execute(stmt)).mappings().all()
    items = [
        {
            'app_id': row['app_id'],
            'name': row['name'],
            'description': row['description'],
            'emoji': row['emoji'],
            'icon_url': row['icon_url'],
            'version': row['version'],
        }
        for row in rows
    ]
    return response_base.success(data=items)
