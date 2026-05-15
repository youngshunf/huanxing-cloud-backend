"""
应用管理服务

负责应用的创建、更新、版本管理等核心操作
"""

from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_manifests import app_manifests_dao
from backend.app.app_platform.crud.crud_app_versions import app_versions_dao
from backend.app.app_platform.model import AppManifests, AppVersions
from backend.common.exception import errors


class AppService:
    """应用管理服务"""

    @staticmethod
    async def create_app(
        db: AsyncSession,
        developer_id: str,
        namespace: str,
        name: str,
        display_name: str,
        description: str,
        manifest_data: dict[str, Any],
    ) -> AppManifests:
        """
        创建应用

        :param db: 数据库会话
        :param developer_id: 开发者 ID
        :param namespace: 命名空间
        :param name: 应用名称
        :param display_name: 显示名称
        :param description: 描述
        :param manifest_data: Manifest 数据
        :return: 应用对象
        """
        # 生成 app_id
        app_id = f"app_{namespace}_{name}"

        # 检查是否已存在
        existing = await app_manifests_dao.get_by_app_id(db, app_id)
        if existing:
            raise errors.BadRequestError(msg=f'应用 {app_id} 已存在')

        # 创建应用
        app = await app_manifests_dao.create(
            db=db,
            obj={
                'app_id': app_id,
                'developer_id': developer_id,
                'namespace': namespace,
                'name': name,
                'display_name': display_name,
                'description': description,
                'current_version': manifest_data.get('version', '0.1.0'),
                'backend_runtime_mode': manifest_data.get('backend_runtime_mode', 'platform_hosted'),
                'frontend_hosting_mode': manifest_data.get('frontend_hosting_mode', 'none'),
                'requested_scopes': manifest_data.get('permissions', {}).get('requested_scopes', []),
                'category': manifest_data.get('category'),
                'tags': manifest_data.get('tags', []),
                'status': 'draft',
            },
        )

        # 创建初始版本
        await AppService.create_version(
            db=db,
            app_id=app_id,
            version=manifest_data.get('version', '0.1.0'),
            manifest_snapshot=manifest_data,
        )

        return app

    @staticmethod
    async def create_version(
        db: AsyncSession,
        app_id: str,
        version: str,
        manifest_snapshot: dict[str, Any],
        changelog: str | None = None,
    ) -> AppVersions:
        """
        创建应用版本

        :param db: 数据库会话
        :param app_id: 应用 ID
        :param version: 版本号
        :param manifest_snapshot: Manifest 快照
        :param changelog: 变更日志
        :return: 版本对象
        """
        # 检查版本是否已存在
        existing = await app_versions_dao.get_by_app_and_version(db, app_id, version)
        if existing:
            raise errors.BadRequestError(msg=f'版本 {version} 已存在')

        # 创建版本
        version_obj = await app_versions_dao.create(
            db=db,
            obj={
                'version_id': str(uuid4()),
                'app_id': app_id,
                'version': version,
                'changelog': changelog,
                'manifest_snapshot': manifest_snapshot,
                'status': 'draft',
            },
        )

        return version_obj

    @staticmethod
    async def get_app(db: AsyncSession, app_id: str) -> AppManifests:
        """
        获取应用

        :param db: 数据库会话
        :param app_id: 应用 ID
        :return: 应用对象
        """
        app = await app_manifests_dao.get_by_app_id(db, app_id)
        if not app:
            raise errors.NotFoundError(msg=f'应用 {app_id} 不存在')
        return app

    @staticmethod
    async def update_app_status(
        db: AsyncSession,
        app_id: str,
        status: str,
    ) -> None:
        """
        更新应用状态

        :param db: 数据库会话
        :param app_id: 应用 ID
        :param status: 新状态
        """
        app = await AppService.get_app(db, app_id)
        await app_manifests_dao.update(
            db=db,
            pk=app.app_id,
            obj={'status': status},
        )


app_service: AppService = AppService()
