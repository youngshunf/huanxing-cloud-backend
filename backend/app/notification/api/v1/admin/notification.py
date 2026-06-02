"""统一通知 Admin 端 API

路由前缀: /api/v1/notifications/admin
认证方式: Admin JWT（DependsJwtAuth）

本轮提供只读运维能力：按接收方 hasn_id 查看通知（含全 category）。
通知发送/删除写操作需 RBAC 权限码，留后续；禁止占位假实现。

注意：FastAPI 端点签名里的 CurrentSession 需运行时解析依赖，故本文件不使用
`from __future__ import annotations`（与社区 Admin API 同惯例）。
"""
from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.notification.service.notification_service import notification_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '/notifications',
    summary='管理端：按接收方查看通知',
    dependencies=[DependsJwtAuth],
)
async def admin_list_notifications(
    db: CurrentSession,
    recipient_hasn_id: Annotated[str, Query(description='接收方 hasn_id')],
    category: Annotated[str | None, Query(description='通知粗类，逗号分隔')] = None,
    unread_only: Annotated[bool, Query()] = False,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ResponseModel:
    categories = [c.strip() for c in category.split(',') if c.strip()] if category else None
    result = await notification_service.list_notifications(
        db,
        recipient_hasn_id=recipient_hasn_id,
        categories=categories,
        unread_only=unread_only,
        cursor=cursor,
        limit=limit,
    )
    return response_base.success(data=result)
