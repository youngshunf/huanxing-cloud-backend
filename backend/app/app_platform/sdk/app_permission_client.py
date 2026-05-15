#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Permission Client

应用权限能力客户端
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.sdk.app_context import AppContext
from backend.app.app_platform.service.permission_service import PermissionService
from backend.app.app_platform.service.permission_validator import PermissionValidator
from backend.common.log import log


class AppPermissionClient:
    """
    应用权限客户端

    提供权限查询和校验能力
    """

    def __init__(self, context: AppContext, db: AsyncSession):
        """
        初始化权限客户端

        :param context: 应用上下文
        :param db: 数据库会话
        """
        self.context = context
        self.db = db
        self.permission_service = PermissionService()
        self.permission_validator = PermissionValidator()

    async def has_permission(self, scope: str) -> bool:
        """
        检查是否有权限

        :param scope: 权限 scope
        :return: 是否有权限
        """
        try:
            await self.permission_validator.validate_permission(
                db=self.db,
                owner_id=self.context.owner_id,
                installation_id=self.context.installation_id,
                scope=scope,
            )
            return True
        except Exception as e:
            log.warning(f"Permission check failed: {e}")
            return False

    async def get_granted_scopes(self) -> list[str]:
        """
        获取已授予的权限列表

        :return: Scope 列表
        """
        return await self.permission_service.get_granted_scopes(
            db=self.db,
            owner_id=self.context.owner_id,
            installation_id=self.context.installation_id,
        )

    async def request_permission(
        self,
        scope: str,
        reason: str,
    ) -> str:
        """
        请求动态权限

        :param scope: 权限 scope
        :param reason: 请求原因
        :return: 请求 ID
        """
        return await self.permission_service.request_dynamic_permission(
            db=self.db,
            installation_id=self.context.installation_id,
            scope=scope,
            reason=reason,
        )

    async def check_permission_status(
        self,
        request_id: str,
    ) -> Optional[str]:
        """
        检查动态权限请求状态

        :param request_id: 请求 ID
        :return: 状态（'pending', 'approved', 'rejected'）
        """
        # TODO: 实现状态查询
        log.info(f"AppPermissionClient.check_permission_status: request_id={request_id}")
        return None
