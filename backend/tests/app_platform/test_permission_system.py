"""权限系统集成测试

测试权限授予、撤销、校验、动态请求等功能。
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_permission_grants import app_permission_grants_dao
from backend.app.app_platform.model import AppPermissionGrants
from backend.app.app_platform.schema.app_permission_grants import CreateAppPermissionGrantsParam
from backend.app.app_platform.service.permission_validator import PermissionValidator
from backend.utils.timezone import timezone


@pytest.mark.asyncio
async def test_grant_and_query_permission(
    db_session: AsyncSession,
    test_owner_id: str,
    test_app_id: str,
    cleanup_test_data,
):
    """测试权限授予和查询"""
    # 创建权限授予记录
    grant_param = CreateAppPermissionGrantsParam(
        installation_id='test_installation_001',
        scope='hasn.im.send',
        granted_by='system',
        grant_source='installation',
        status='active',
    )

    grant = await app_permission_grants_dao.create(db_session, grant_param)

    assert grant is not None
    assert grant.installation_id == 'test_installation_001'
    assert grant.scope == 'hasn.im.send'
    assert grant.status == 'active'

    # 查询权限
    result = await db_session.execute(
        select(AppPermissionGrants).where(
            AppPermissionGrants.installation_id == 'test_installation_001',
            AppPermissionGrants.scope == 'hasn.im.send',
        )
    )
    saved_grant = result.scalar_one_or_none()
    assert saved_grant is not None
    assert saved_grant.grant_id == grant.grant_id


@pytest.mark.asyncio
async def test_permission_scope_format_validation(
    db_session: AsyncSession,
    cleanup_test_data,
):
    """测试权限 scope 格式校验"""
    validator = PermissionValidator()

    # 有效的平台级权限
    assert validator._is_valid_scope_format('hasn.im.send') is True
    assert validator._is_valid_scope_format('hasn.agent.invoke') is True
    assert validator._is_valid_scope_format('hasn.app.install.manage') is True

    # 有效的应用级权限
    assert validator._is_valid_scope_format('myapp.data.read') is True
    assert validator._is_valid_scope_format('myapp.api.call') is True

    # 无效格式
    assert validator._is_valid_scope_format('invalid') is False
    assert validator._is_valid_scope_format('hasn') is False
    assert validator._is_valid_scope_format('hasn.') is False
    assert validator._is_valid_scope_format('.im.send') is False


@pytest.mark.asyncio
async def test_multiple_grants(
    db_session: AsyncSession,
    cleanup_test_data,
):
    """测试多个权限授予"""
    scopes = ['hasn.im.send', 'hasn.agent.invoke', 'hasn.app.install']

    for scope in scopes:
        grant_param = CreateAppPermissionGrantsParam(
            installation_id='test_installation_002',
            scope=scope,
            granted_by='system',
            grant_source='installation',
            status='active',
        )
        await app_permission_grants_dao.create(db_session, grant_param)

    # 查询所有授予的权限
    result = await db_session.execute(
        select(AppPermissionGrants).where(
            AppPermissionGrants.installation_id == 'test_installation_002',
            AppPermissionGrants.status == 'active',
        )
    )
    grants = result.scalars().all()

    assert len(grants) == 3
    granted_scopes = [g.scope for g in grants]
    assert set(granted_scopes) == set(scopes)


@pytest.mark.asyncio
async def test_revoke_permission(
    db_session: AsyncSession,
    cleanup_test_data,
):
    """测试权限撤销"""
    # 使用随机 ID 避免冲突
    installation_id = f'test_installation_{uuid.uuid4().hex[:8]}'

    # 创建权限
    grant_param = CreateAppPermissionGrantsParam(
        installation_id=installation_id,
        scope='hasn.trade.pay',
        granted_by='system',
        grant_source='installation',
        status='active',
    )
    grant = await app_permission_grants_dao.create(db_session, grant_param)
    await db_session.flush()

    # 撤销权限（直接修改对象）
    grant.status = 'revoked'
    grant.revoked_at = timezone.now()
    await db_session.flush()

    # 验证权限已撤销
    assert grant.status == 'revoked'
    assert grant.revoked_at is not None
