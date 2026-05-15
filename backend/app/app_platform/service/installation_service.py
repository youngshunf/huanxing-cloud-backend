"""
安装管理服务

负责应用的安装、卸载、更新等操作
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_installations import app_installations_dao
from backend.app.app_platform.model import AppInstallations
from backend.app.app_platform.service.permission_service import permission_service
from backend.common.exception import errors


class InstallationService:
    """安装管理服务"""

    @staticmethod
    async def install_app(
        db: AsyncSession,
        owner_id: str,
        app_id: str,
        listing_id: str,
        version: str,
        granted_scopes: list[str],
    ) -> AppInstallations:
        """
        安装应用

        :param db: 数据库会话
        :param owner_id: Owner ID
        :param app_id: App ID
        :param listing_id: Listing ID
        :param version: 安装的版本
        :param granted_scopes: 授予的权限列表
        :return: Installation 对象
        """
        # 生成 installation_id
        installation_id = f"appi_{uuid4().hex[:16]}"

        # 创建 Installation
        installation = await app_installations_dao.create(
            db=db,
            obj={
                'installation_id': installation_id,
                'owner_id': owner_id,
                'app_id': app_id,
                'listing_id': listing_id,
                'installed_version': version,
                'granted_scopes': granted_scopes,
                'status': 'active',
                'installed_at': datetime.utcnow(),
            },
        )

        # 授予权限
        await permission_service.grant_scopes(
            db=db,
            installation_id=installation_id,
            scopes=granted_scopes,
            granted_by=owner_id,
            grant_source='installation',
        )

        return installation

    @staticmethod
    async def uninstall_app(
        db: AsyncSession,
        installation_id: str,
        owner_id: str,
    ) -> None:
        """
        卸载应用

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param owner_id: Owner ID
        """
        installation = await app_installations_dao.get_by_installation_id(db, installation_id)
        if not installation:
            raise errors.NotFoundError(msg=f'Installation {installation_id} 不存在')

        if installation.owner_id != owner_id:
            raise errors.ForbiddenError(msg='无权卸载此应用')

        # 更新状态为 revoked
        await app_installations_dao.update(
            db=db,
            pk=installation_id,
            obj={
                'status': 'revoked',
            },
        )

    @staticmethod
    async def get_installation(
        db: AsyncSession,
        installation_id: str,
    ) -> AppInstallations:
        """
        获取 Installation

        :param db: 数据库会话
        :param installation_id: Installation ID
        :return: Installation 对象
        """
        installation = await app_installations_dao.get_by_installation_id(db, installation_id)
        if not installation:
            raise errors.NotFoundError(msg=f'Installation {installation_id} 不存在')
        return installation

    @staticmethod
    async def list_installations_by_owner(
        db: AsyncSession,
        owner_id: str,
    ) -> list[AppInstallations]:
        """
        列出 Owner 的所有 Installation

        :param db: 数据库会话
        :param owner_id: Owner ID
        :return: Installation 列表
        """
        return await app_installations_dao.get_by_owner(db, owner_id)


installation_service: InstallationService = InstallationService()
