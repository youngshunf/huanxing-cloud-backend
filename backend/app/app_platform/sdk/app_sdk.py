#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App SDK

应用平台 SDK 工厂类
"""
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.sdk.app_context import AppContext
from backend.app.app_platform.sdk.app_data_client import AppDataClient
from backend.app.app_platform.sdk.app_audit_client import AppAuditClient
from backend.app.app_platform.sdk.app_permission_client import AppPermissionClient


class AppSDK:
    """
    应用平台 SDK

    提供统一的 SDK 入口，包含所有客户端能力
    """

    def __init__(self, context: AppContext, db: AsyncSession):
        """
        初始化 SDK

        :param context: 应用上下文
        :param db: 数据库会话
        """
        self.context = context
        self.db = db

        # 初始化各个客户端
        self.data = AppDataClient(context, db)
        self.audit = AppAuditClient(context, db)
        self.permission = AppPermissionClient(context, db)

    @classmethod
    def create(
        cls,
        owner_id: str,
        app_id: str,
        installation_id: str,
        db: AsyncSession,
        **kwargs,
    ) -> 'AppSDK':
        """
        创建 SDK 实例

        :param owner_id: Owner ID
        :param app_id: App ID
        :param installation_id: Installation ID
        :param db: 数据库会话
        :param kwargs: 其他上下文参数
        :return: SDK 实例
        """
        context = AppContext(
            owner_id=owner_id,
            app_id=app_id,
            installation_id=installation_id,
            **kwargs,
        )
        return cls(context, db)

    def get_context(self) -> AppContext:
        """获取应用上下文"""
        return self.context

    def get_isolation_key(self) -> str:
        """获取数据隔离键"""
        return self.context.get_isolation_key()
