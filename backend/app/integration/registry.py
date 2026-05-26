"""
第三方应用集成注册表

负责管理和实例化所有集成类
"""
from typing import Dict, Type

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integration.base import BaseIntegration
from backend.app.integration.crud.crud_integration_apps import integration_apps_dao


class IntegrationRegistry:
    """集成类注册表"""

    def __init__(self):
        self._integration_classes: Dict[str, Type[BaseIntegration]] = {}

    def register(self, app_type: str, integration_class: Type[BaseIntegration]):
        """
        注册集成类

        Args:
            app_type: 应用类型（如 clawhub、github、feishu）
            integration_class: 集成类（必须继承 BaseIntegration）
        """
        if not issubclass(integration_class, BaseIntegration):
            raise TypeError(f"{integration_class} must inherit from BaseIntegration")
        self._integration_classes[app_type] = integration_class

    async def get(self, db: AsyncSession, app_id: str) -> BaseIntegration:
        """
        获取集成实例（从数据库加载配置）

        Args:
            db: 数据库会话
            app_id: 应用唯一标识

        Returns:
            集成实例

        Raises:
            ValueError: 应用不存在或未启用
            KeyError: 应用类型未注册
        """
        # 从数据库加载应用配置
        app = await integration_apps_dao.get_by_app_id(db, app_id)
        if not app:
            raise ValueError(f"Application {app_id} not found")
        if not app.is_enabled:
            raise ValueError(f"Application {app_id} is disabled")

        # 获取对应的集成类
        integration_class = self._integration_classes.get(app.app_type)
        if not integration_class:
            raise KeyError(
                f"Integration class for app_type '{app.app_type}' not registered. "
                f"Available types: {list(self._integration_classes.keys())}"
            )

        # 实例化集成类
        config = {
            "base_url": app.base_url,
            **(app.config or {}),
        }
        return integration_class(app_id=app.app_id, config=config)

    def list_registered_types(self) -> list[str]:
        """
        列出所有已注册的应用类型

        Returns:
            应用类型列表
        """
        return list(self._integration_classes.keys())


# 全局注册表实例
registry = IntegrationRegistry()
