"""
第三方应用集成抽象基类

定义所有第三方应用集成必须实现的接口
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class BaseIntegration(ABC):
    """第三方应用集成抽象基类"""

    def __init__(self, app_id: str, config: Dict[str, Any]):
        """
        初始化集成实例

        Args:
            app_id: 应用唯一标识
            config: 应用配置（从数据库加载）
        """
        self.app_id = app_id
        self.config = config
        self.base_url = config.get("base_url", "")

    @abstractmethod
    async def auto_register_user(
        self,
        db: AsyncSession,
        user_id: int,
        username: str,
        email: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        自动注册用户到第三方平台

        Args:
            db: 数据库会话
            user_id: 唤星用户 ID
            username: 用户名
            email: 邮箱（可选）
            **kwargs: 其他平台特定参数

        Returns:
            包含凭证信息的字典，例如：
            {
                "api_key": "xxx",
                "user_id": "xxx",
                "expires_at": "2024-12-31T23:59:59Z"
            }

        Raises:
            Exception: 注册失败时抛出异常
        """
        pass

    @abstractmethod
    async def generate_login_token(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> str:
        """
        生成一次性登录 Token（用于 iframe 自动登录）

        Args:
            db: 数据库会话
            user_id: 唤星用户 ID
            **kwargs: 其他平台特定参数

        Returns:
            一次性登录 Token（通常 5 分钟有效）

        Raises:
            Exception: 生成失败时抛出异常
        """
        pass

    @abstractmethod
    async def revoke_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> bool:
        """
        撤销用户凭证（断开连接）

        Args:
            db: 数据库会话
            user_id: 唤星用户 ID
            **kwargs: 其他平台特定参数

        Returns:
            是否成功撤销

        Raises:
            Exception: 撤销失败时抛出异常
        """
        pass

    @abstractmethod
    async def refresh_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        刷新用户凭证（如果支持）

        Args:
            db: 数据库会话
            user_id: 唤星用户 ID
            **kwargs: 其他平台特定参数

        Returns:
            新的凭证信息

        Raises:
            Exception: 刷新失败时抛出异常
        """
        pass

    async def validate_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        credentials: Dict[str, Any],
        **kwargs
    ) -> bool:
        """
        验证凭证是否有效（可选实现）

        Args:
            db: 数据库会话
            user_id: 唤星用户 ID
            credentials: 凭证信息
            **kwargs: 其他平台特定参数

        Returns:
            凭证是否有效
        """
        return True

    def get_iframe_url(self, login_token: str) -> str:
        """
        获取 iframe 嵌入 URL（带自动登录 Token）

        Args:
            login_token: 一次性登录 Token

        Returns:
            完整的 iframe URL
        """
        return f"{self.base_url}/auth/token-login?token={login_token}"
