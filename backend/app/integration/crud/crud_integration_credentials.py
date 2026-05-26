from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.integration.model import IntegrationCredentials
from backend.app.integration.schema.integration_credentials import CreateIntegrationCredentialsParam, UpdateIntegrationCredentialsParam


class CRUDIntegrationCredentials(CRUDPlus[IntegrationCredentials]):
    async def get_by_user_and_app(
        self, db: AsyncSession, user_id: int, app_id: str
    ) -> IntegrationCredentials | None:
        """
        根据用户 ID 和应用 ID 获取凭证

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param app_id: 应用 ID
        :return:
        """
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.app_id == app_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get(self, db: AsyncSession, pk: int) -> IntegrationCredentials | None:
        """
        获取用户第三方应用凭证

        :param db: 数据库会话
        :param pk: 用户第三方应用凭证 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取用户第三方应用凭证列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[IntegrationCredentials]:
        """
        获取所有用户第三方应用凭证

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateIntegrationCredentialsParam) -> None:
        """
        创建用户第三方应用凭证

        :param db: 数据库会话
        :param obj: 创建用户第三方应用凭证参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateIntegrationCredentialsParam) -> int:
        """
        更新用户第三方应用凭证

        :param db: 数据库会话
        :param pk: 用户第三方应用凭证 ID
        :param obj: 更新 用户第三方应用凭证参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除用户第三方应用凭证

        :param db: 数据库会话
        :param pks: 用户第三方应用凭证 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


integration_credentials_dao: CRUDIntegrationCredentials = CRUDIntegrationCredentials(IntegrationCredentials)
