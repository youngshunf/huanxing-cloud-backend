"""
ClawHub 镜像站集成实现
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integration.base import BaseIntegration
from backend.app.integration.crud.crud_integration_credentials import integration_credentials_dao
from backend.app.integration.schema.integration_credentials import CreateIntegrationCredentialsParam, UpdateIntegrationCredentialsParam
from backend.common.log import log


class ClawHubIntegration(BaseIntegration):
    """ClawHub 镜像站集成"""

    async def auto_register_user(
        self,
        db: AsyncSession,
        user_id: int,
        username: str,
        email: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        自动注册用户到 ClawHub 镜像站

        调用 ClawHub 的 autoRegister mutation
        """
        # 检查是否已经注册过
        existing = await integration_credentials_dao.get_by_user_and_app(
            db, user_id, self.app_id
        )
        if existing and existing.is_active:
            log.info(f"User {user_id} already registered to ClawHub")
            return existing.credentials

        # 调用 ClawHub 自动注册 API
        register_url = f"{self.base_url}/api/huanxing/auto-register"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    register_url,
                    json={
                        "huanxing_user_id": str(user_id),
                        "username": username,
                        "email": email or f"user{user_id}@huanxing.ai",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                # 提取凭证信息
                credentials = {
                    "api_key": data["apiKey"],
                    "clawhub_user_id": data.get("userId"),
                }

                # 保存到数据库
                if existing:
                    # 更新现有记录
                    await integration_credentials_dao.update_model(
                        db,
                        existing.id,
                        UpdateIntegrationCredentialsParam(
                            user_id=user_id,
                            app_id=self.app_id,
                            credentials=credentials,
                            is_active=True,
                            expires_at=None,
                        ),
                    )
                else:
                    # 创建新记录
                    await integration_credentials_dao.create_model(
                        db,
                        CreateIntegrationCredentialsParam(
                            user_id=user_id,
                            app_id=self.app_id,
                            credentials=credentials,
                            is_active=True,
                            expires_at=None,
                        ),
                    )

                log.info(f"User {user_id} registered to ClawHub successfully")
                return credentials

            except httpx.HTTPError as e:
                log.error(f"Failed to register user {user_id} to ClawHub: {e}")
                raise Exception(f"ClawHub registration failed: {str(e)}")

    async def generate_login_token(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> str:
        """
        生成一次性登录 Token

        调用 ClawHub 的 generateLoginToken mutation
        """
        # 获取用户凭证
        cred = await integration_credentials_dao.get_by_user_and_app(
            db, user_id, self.app_id
        )
        if not cred or not cred.is_active:
            raise ValueError(f"User {user_id} not connected to ClawHub")

        api_key = cred.credentials.get("api_key")
        if not api_key:
            raise ValueError("API key not found in credentials")

        # 调用 ClawHub 生成登录 Token API
        token_url = f"{self.base_url}/api/huanxing/generate-login-token"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    token_url,
                    json={"api_key": api_key},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                login_token = data["token"]
                log.info(f"Generated login token for user {user_id}")
                return login_token

            except httpx.HTTPError as e:
                log.error(f"Failed to generate login token for user {user_id}: {e}")
                raise Exception(f"Token generation failed: {str(e)}")

    async def revoke_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> bool:
        """
        撤销用户凭证（断开连接）

        将数据库中的凭证标记为 inactive
        """
        cred = await integration_credentials_dao.get_by_user_and_app(
            db, user_id, self.app_id
        )
        if not cred:
            return True  # 已经不存在，视为成功

        await integration_credentials_dao.update_model(
            db,
            cred.id,
            UpdateIntegrationCredentialsParam(
                user_id=user_id,
                app_id=self.app_id,
                credentials=cred.credentials,
                is_active=False,
                expires_at=cred.expires_at,
            ),
        )

        log.info(f"Revoked ClawHub credentials for user {user_id}")
        return True

    async def refresh_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        刷新用户凭证

        ClawHub 使用永久 API Key，不需要刷新
        """
        cred = await integration_credentials_dao.get_by_user_and_app(
            db, user_id, self.app_id
        )
        if not cred or not cred.is_active:
            raise ValueError(f"User {user_id} not connected to ClawHub")

        return cred.credentials

    async def validate_credentials(
        self,
        db: AsyncSession,
        user_id: int,
        credentials: Dict[str, Any],
        **kwargs
    ) -> bool:
        """
        验证凭证是否有效

        调用 ClawHub API 验证 API Key
        """
        api_key = credentials.get("api_key")
        if not api_key:
            return False

        # 调用 ClawHub 验证 API
        validate_url = f"{self.base_url}/api/huanxing/validate-key"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    validate_url,
                    json={"api_key": api_key},
                    timeout=10.0,
                )
                return response.status_code == 200
            except httpx.HTTPError:
                return False
