"""
权限管理服务

负责权限的授予、撤销、查询等核心操作
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_dynamic_permission_requests import app_dynamic_permission_requests_dao
from backend.app.app_platform.crud.crud_app_permission_grants import app_permission_grants_dao
from backend.app.app_platform.model import AppPermissionGrants
from backend.app.app_platform.schema.app_permission_grants import CreateAppPermissionGrantsParam
from backend.common.exception import errors


class PermissionService:
    """权限管理服务"""

    @staticmethod
    async def grant_scopes(
        db: AsyncSession,
        installation_id: str,
        scopes: list[str],
        granted_by: str,
        grant_source: str = 'installation',
    ) -> list[AppPermissionGrants]:
        """
        授予权限

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param scopes: 权限列表
        :param granted_by: 授予者 Owner ID
        :param grant_source: 授予来源
        :return: 授予记录列表
        """
        grants = []
        for scope in scopes:
            # 检查是否已存在活跃的授权
            existing_grant = await app_permission_grants_dao.get_by_installation_and_scope(
                db=db,
                installation_id=installation_id,
                scope=scope,
            )

            if existing_grant and existing_grant.status == 'active':
                grants.append(existing_grant)
                continue

            # 创建新的授权记录
            grant_param = CreateAppPermissionGrantsParam(
                installation_id=installation_id,
                scope=scope,
                granted_by=granted_by,
                grant_source=grant_source,
                status='active',
            )
            grant = await app_permission_grants_dao.create(db, grant_param)
            grants.append(grant)

        return grants

    @staticmethod
    async def revoke_scope(
        db: AsyncSession,
        installation_id: str,
        scope: str,
        revoked_by: str,
        revocation_reason: str | None = None,
    ) -> None:
        """
        撤销权限

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param scope: 权限标识
        :param revoked_by: 撤销者（'owner' 或 'platform'）
        :param revocation_reason: 撤销原因
        """
        grant = await app_permission_grants_dao.get_by_installation_and_scope(
            db=db,
            installation_id=installation_id,
            scope=scope,
        )

        if not grant:
            raise errors.NotFoundError(msg=f'权限授予记录不存在: {scope}')

        if grant.status == 'revoked':
            return  # 已经撤销

        # 更新为撤销状态
        await app_permission_grants_dao.update(
            db=db,
            pk=grant.grant_id,
            obj={
                'status': 'revoked',
                'revoked_at': datetime.utcnow(),
                'revoked_by': revoked_by,
                'revocation_reason': revocation_reason,
            },
        )

    @staticmethod
    async def request_dynamic_permission(
        db: AsyncSession,
        installation_id: str,
        scope: str,
        request_reason: str,
        request_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        动态请求权限

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param scope: 权限标识
        :param request_reason: 请求原因
        :param request_context: 请求上下文
        :return: 请求结果
        """
        # 检查是否已有该权限
        grant = await app_permission_grants_dao.get_by_installation_and_scope(
            db=db,
            installation_id=installation_id,
            scope=scope,
        )

        if grant and grant.status == 'active':
            return {'status': 'already_granted', 'scope': scope}

        # 创建权限请求记录
        request_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=24)  # 24小时后过期

        await app_dynamic_permission_requests_dao.create(
            db=db,
            obj={
                'request_id': request_id,
                'installation_id': installation_id,
                'scope': scope,
                'request_reason': request_reason,
                'request_context': request_context,
                'status': 'pending',
                'expires_at': expires_at,
            },
        )

        # TODO: 发送通知给 Owner

        return {
            'status': 'pending',
            'request_id': request_id,
            'message': '权限请求已发送给 Owner，请等待批准',
        }

    @staticmethod
    async def approve_dynamic_permission_request(
        db: AsyncSession,
        request_id: str,
        decided_by: str,
        decision_reason: str | None = None,
    ) -> None:
        """
        批准动态权限请求

        :param db: 数据库会话
        :param request_id: 请求 ID
        :param decided_by: 决策者 Owner ID
        :param decision_reason: 决策理由
        """
        request = await app_dynamic_permission_requests_dao.get(db, request_id)
        if not request:
            raise errors.NotFoundError(msg='权限请求不存在')

        if request.status != 'pending':
            raise errors.BadRequestError(msg=f'权限请求状态不正确: {request.status}')

        # 更新请求状态
        await app_dynamic_permission_requests_dao.update(
            db=db,
            pk=request_id,
            obj={
                'status': 'approved',
                'decided_at': datetime.utcnow(),
                'decided_by': decided_by,
                'decision_reason': decision_reason,
            },
        )

        # 授予权限
        await PermissionService.grant_scopes(
            db=db,
            installation_id=request.installation_id,
            scopes=[request.scope],
            granted_by=decided_by,
            grant_source='dynamic_request',
        )

    @staticmethod
    async def deny_dynamic_permission_request(
        db: AsyncSession,
        request_id: str,
        decided_by: str,
        decision_reason: str | None = None,
    ) -> None:
        """
        拒绝动态权限请求

        :param db: 数据库会话
        :param request_id: 请求 ID
        :param decided_by: 决策者 Owner ID
        :param decision_reason: 决策理由
        """
        request = await app_dynamic_permission_requests_dao.get(db, request_id)
        if not request:
            raise errors.NotFoundError(msg='权限请求不存在')

        if request.status != 'pending':
            raise errors.BadRequestError(msg=f'权限请求状态不正确: {request.status}')

        # 更新请求状态
        await app_dynamic_permission_requests_dao.update(
            db=db,
            pk=request_id,
            obj={
                'status': 'denied',
                'decided_at': datetime.utcnow(),
                'decided_by': decided_by,
                'decision_reason': decision_reason,
            },
        )


permission_service: PermissionService = PermissionService()
