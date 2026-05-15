"""应用管理集成测试

测试应用创建、版本管理、安装等功能。
"""
from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_developers import app_developers_dao
from backend.app.app_platform.crud.crud_app_installations import app_installations_dao
from backend.app.app_platform.crud.crud_app_manifests import app_manifests_dao
from backend.app.app_platform.crud.crud_app_versions import app_versions_dao
from backend.app.app_platform.model import AppDevelopers, AppInstallations, AppManifests, AppVersions
from backend.app.app_platform.schema.app_developers import CreateAppDevelopersParam
from backend.app.app_platform.schema.app_installations import CreateAppInstallationsParam
from backend.app.app_platform.schema.app_manifests import CreateAppManifestsParam
from backend.app.app_platform.schema.app_versions import CreateAppVersionsParam


@pytest.mark.asyncio
async def test_create_developer_and_app(
    db_session: AsyncSession,
    test_owner_id: str,
    cleanup_test_data,
):
    """测试创建开发者和应用"""
    # 创建开发者
    developer_param = CreateAppDevelopersParam(
        owner_id=test_owner_id,
        developer_name='Test Developer',
        developer_type='individual',
        status='active',
    )
    developer = await app_developers_dao.create(db_session, developer_param)

    assert developer is not None
    assert developer.owner_id == test_owner_id
    assert developer.developer_name == 'Test Developer'

    # 创建应用
    app_param = CreateAppManifestsParam(
        app_id='test_app_001',
        app_name='Test App',
        developer_id=developer.id,
        category='productivity',
        description='A test application',
        status='draft',
    )
    app = await app_manifests_dao.create(db_session, app_param)

    assert app is not None
    assert app.app_id == 'test_app_001'
    assert app.app_name == 'Test App'
    assert app.status == 'draft'


@pytest.mark.asyncio
async def test_create_app_version(
    db_session: AsyncSession,
    test_owner_id: str,
    cleanup_test_data,
):
    """测试创建应用版本"""
    # 创建开发者
    developer_param = CreateAppDevelopersParam(
        owner_id=test_owner_id,
        developer_name='Test Developer',
        developer_type='individual',
        status='active',
    )
    developer = await app_developers_dao.create(db_session, developer_param)

    # 创建应用
    app_param = CreateAppManifestsParam(
        app_id='test_app_002',
        app_name='Test App 2',
        developer_id=developer.id,
        category='productivity',
        status='published',
    )
    app = await app_manifests_dao.create(db_session, app_param)

    # 创建版本
    version_param = CreateAppVersionsParam(
        app_id='test_app_002',
        version='1.0.0',
        release_notes='Initial release',
        status='published',
    )
    version = await app_versions_dao.create(db_session, version_param)

    assert version is not None
    assert version.version == '1.0.0'
    assert version.status == 'published'


@pytest.mark.asyncio
async def test_install_app(
    db_session: AsyncSession,
    test_owner_id: str,
    cleanup_test_data,
):
    """测试安装应用"""
    # 创建开发者
    developer_param = CreateAppDevelopersParam(
        owner_id=test_owner_id,
        developer_name='Test Developer',
        developer_type='individual',
        status='active',
    )
    developer = await app_developers_dao.create(db_session, developer_param)

    # 创建应用
    app_param = CreateAppManifestsParam(
        app_id='test_app_003',
        app_name='Test App 3',
        developer_id=developer.id,
        category='productivity',
        status='published',
    )
    app = await app_manifests_dao.create(db_session, app_param)

    # 创建版本
    version_param = CreateAppVersionsParam(
        app_id='test_app_003',
        version='1.0.0',
        status='published',
    )
    version = await app_versions_dao.create(db_session, version_param)

    # 安装应用
    installation_param = CreateAppInstallationsParam(
        owner_id=test_owner_id,
        app_id='test_app_003',
        version='1.0.0',
        status='active',
    )
    installation = await app_installations_dao.create(db_session, installation_param)

    assert installation is not None
    assert installation.owner_id == test_owner_id
    assert installation.app_id == 'test_app_003'
    assert installation.version == '1.0.0'
    assert installation.status == 'active'


@pytest.mark.asyncio
async def test_list_installed_apps(
    db_session: AsyncSession,
    test_owner_id: str,
    cleanup_test_data,
):
    """测试列出已安装应用"""
    # 创建开发者
    developer_param = CreateAppDevelopersParam(
        owner_id=test_owner_id,
        developer_name='Test Developer',
        developer_type='individual',
        status='active',
    )
    developer = await app_developers_dao.create(db_session, developer_param)

    # 创建多个应用和安装记录
    for i in range(3):
        app_param = CreateAppManifestsParam(
            app_id=f'test_app_00{i+4}',
            app_name=f'Test App {i+4}',
            developer_id=developer.id,
            category='productivity',
            status='published',
        )
        await app_manifests_dao.create(db_session, app_param)

        installation_param = CreateAppInstallationsParam(
            owner_id=test_owner_id,
            app_id=f'test_app_00{i+4}',
            version='1.0.0',
            status='active',
        )
        await app_installations_dao.create(db_session, installation_param)

    # 列出已安装应用
    result = await db_session.execute(
        select(AppInstallations).where(
            AppInstallations.owner_id == test_owner_id,
            AppInstallations.status == 'active',
        )
    )
    installed = result.scalars().all()

    assert len(installed) == 3
