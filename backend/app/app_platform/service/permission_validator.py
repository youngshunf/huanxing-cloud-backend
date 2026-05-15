"""
权限校验服务

根据风险等级执行不同的校验策略：
- Low: 只检查 scope 是否存在
- Medium: scope 检查 + 限流
- High: scope 检查 + 限流 + Owner 二次确认
"""

import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_permission_grants import app_permission_grants_dao
from backend.app.app_platform.crud.crud_platform_scopes import platform_scopes_dao
from backend.common.exception import errors


class PermissionValidator:
    """权限校验器"""

    # Scope 格式正则：至少 3 段，每段由小写字母、数字、下划线组成
    SCOPE_PATTERN = re.compile(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){2,}$')

    @staticmethod
    def _is_valid_scope_format(scope: str) -> bool:
        """
        验证 scope 格式是否有效

        :param scope: 权限标识
        :return: 是否有效
        """
        if not scope:
            return False
        return bool(PermissionValidator.SCOPE_PATTERN.match(scope))

    @staticmethod
    async def check_scopes(
        db: AsyncSession,
        installation_id: str,
        required_scopes: list[str],
        action_context: dict[str, Any] | None = None,
    ) -> None:
        """
        检查 Installation 是否拥有所需权限

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param required_scopes: 所需权限列表
        :param action_context: 操作上下文
        :raises: PermissionError 如果权限不足
        """
        if not required_scopes:
            return

        for scope in required_scopes:
            await PermissionValidator._check_single_scope(
                db=db,
                installation_id=installation_id,
                scope=scope,
                action_context=action_context or {},
            )

    @staticmethod
    async def _check_single_scope(
        db: AsyncSession,
        installation_id: str,
        scope: str,
        action_context: dict[str, Any],
    ) -> None:
        """
        检查单个权限

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param scope: 权限标识
        :param action_context: 操作上下文
        """
        # 1. 检查权限是否已授予
        grant = await app_permission_grants_dao.get_by_installation_and_scope(
            db=db,
            installation_id=installation_id,
            scope=scope,
        )

        if not grant or grant.status != 'active':
            raise errors.ForbiddenError(
                msg=f'缺少必需的权限: {scope}',
                data={'error_code': 'ERR_APP_SCOPE_DENIED', 'scope': scope},
            )

        # 2. 获取权限的风险等级
        risk_level = await PermissionValidator._get_scope_risk_level(db, scope)

        # 3. 根据风险等级执行不同策略
        if risk_level == 'low':
            # 低风险：只检查 scope 是否存在（已通过）
            pass

        elif risk_level == 'medium':
            # 中风险：检查限流
            # TODO: 实现限流检查
            pass

        elif risk_level == 'high':
            # 高风险：检查限流 + Owner 确认
            # TODO: 实现限流检查
            # TODO: 实现 Owner 确认
            pass

    @staticmethod
    async def _get_scope_risk_level(db: AsyncSession, scope: str) -> str:
        """
        获取权限的风险等级

        :param db: 数据库会话
        :param scope: 权限标识
        :return: 风险等级 ('low' | 'medium' | 'high')
        """
        # 查询平台权限定义
        platform_scope = await platform_scopes_dao.get_by_scope(db, scope)
        if platform_scope:
            return platform_scope.risk_level

        # 应用权限的风险等级推断
        if scope.endswith('.read'):
            return 'low'
        elif scope.endswith('.write') or scope.endswith('.delete'):
            return 'medium'
        elif scope.endswith('.execute'):
            return 'medium'
        else:
            return 'medium'  # 默认中风险


permission_validator: PermissionValidator = PermissionValidator()
