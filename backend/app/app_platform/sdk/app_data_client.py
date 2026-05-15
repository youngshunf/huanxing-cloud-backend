#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Data Client

应用数据能力客户端，提供 Resource 存储能力
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.sdk.app_context import AppContext
from backend.app.app_platform.crud.crud_app_data_records import CRUDAppDataRecords
from backend.app.app_platform.schema.app_data_records import CreateAppDataRecordsParam, UpdateAppDataRecordsParam
from backend.common.log import log


class AppDataClient:
    """
    应用数据客户端

    提供基于 Resource 的 JSONB 存储能力
    Phase 1: 使用 app_data_records 表（JSONB）
    Phase 2+: 支持升级为专用物理表
    """

    def __init__(self, context: AppContext, db: AsyncSession):
        """
        初始化数据客户端

        :param context: 应用上下文
        :param db: 数据库会话
        """
        self.context = context
        self.db = db
        self.crud = CRUDAppDataRecords()

    async def get(
        self,
        resource_id: str,
        record_key: str,
    ) -> Optional[dict[str, Any]]:
        """
        获取数据记录

        :param resource_id: Resource ID
        :param record_key: 记录键
        :return: 数据 JSON，不存在返回 None
        """
        record = await self.crud.get_by_key(
            db=self.db,
            owner_id=self.context.owner_id,
            app_id=self.context.app_id,
            installation_id=self.context.installation_id,
            resource_id=resource_id,
            record_key=record_key,
        )
        return record.data_json if record else None

    async def set(
        self,
        resource_id: str,
        record_key: str,
        data: dict[str, Any],
    ) -> str:
        """
        设置数据记录

        :param resource_id: Resource ID
        :param record_key: 记录键
        :param data: 数据 JSON
        :return: 记录 ID
        """
        # 检查是否已存在
        existing = await self.crud.get_by_key(
            db=self.db,
            owner_id=self.context.owner_id,
            app_id=self.context.app_id,
            installation_id=self.context.installation_id,
            resource_id=resource_id,
            record_key=record_key,
        )

        if existing:
            # 更新
            await self.crud.update(
                db=self.db,
                pk=existing.id,
                obj=UpdateAppDataRecordsParam(
                    data_json=data,
                    updated_by=self.context.owner_id,
                ),
            )
            return str(existing.id)
        else:
            # 创建
            record = await self.crud.create(
                db=self.db,
                obj=CreateAppDataRecordsParam(
                    owner_id=self.context.owner_id,
                    app_id=self.context.app_id,
                    installation_id=self.context.installation_id,
                    install_target_type=self.context.install_target_type,
                    install_target_id=self.context.install_target_id,
                    resource_id=resource_id,
                    record_key=record_key,
                    data_json=data,
                    created_by=self.context.owner_id,
                ),
            )
            return str(record.id)

    async def delete(
        self,
        resource_id: str,
        record_key: str,
    ) -> bool:
        """
        删除数据记录

        :param resource_id: Resource ID
        :param record_key: 记录键
        :return: 是否删除成功
        """
        count = await self.crud.delete_by_key(
            db=self.db,
            owner_id=self.context.owner_id,
            app_id=self.context.app_id,
            installation_id=self.context.installation_id,
            resource_id=resource_id,
            record_key=record_key,
        )
        return count > 0

    async def list(
        self,
        resource_id: str,
        prefix: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        列出数据记录

        :param resource_id: Resource ID
        :param prefix: 记录键前缀（可选）
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 数据记录列表
        """
        records = await self.crud.list_by_resource(
            db=self.db,
            owner_id=self.context.owner_id,
            app_id=self.context.app_id,
            installation_id=self.context.installation_id,
            resource_id=resource_id,
            prefix=prefix,
        )
        return [
            {
                'record_key': record.record_key,
                'data': record.data_json,
                'created_at': record.created_at.isoformat() if record.created_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None,
            }
            for record in records
        ]

    async def query(
        self,
        resource_id: str,
        filter_json: dict[str, Any],
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        查询数据记录（JSONB 查询）

        :param resource_id: Resource ID
        :param filter_json: JSONB 过滤条件
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 数据记录列表
        """
        # TODO: 实现 JSONB 查询逻辑
        # 需要先创建 app_data_records 表
        log.info(
            f"AppDataClient.query: resource_id={resource_id}, filter={filter_json}, "
            f"limit={limit}, offset={offset}, isolation_key={self.context.get_isolation_key()}"
        )
        return []
