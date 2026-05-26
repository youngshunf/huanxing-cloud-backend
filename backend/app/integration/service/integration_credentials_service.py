from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integration.crud.crud_integration_credentials import integration_credentials_dao
from backend.app.integration.model import IntegrationCredentials
from backend.app.integration.schema.integration_credentials import CreateIntegrationCredentialsParam, DeleteIntegrationCredentialsParam, UpdateIntegrationCredentialsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class IntegrationCredentialsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> IntegrationCredentials:
        """
        获取用户第三方应用凭证

        :param db: 数据库会话
        :param pk: 用户第三方应用凭证 ID
        :return:
        """
        integration_credentials = await integration_credentials_dao.get(db, pk)
        if not integration_credentials:
            raise errors.NotFoundError(msg='用户第三方应用凭证不存在')
        return integration_credentials

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取用户第三方应用凭证列表

        :param db: 数据库会话
        :return:
        """
        integration_credentials_select = await integration_credentials_dao.get_select()
        return await paging_data(db, integration_credentials_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[IntegrationCredentials]:
        """
        获取所有用户第三方应用凭证

        :param db: 数据库会话
        :return:
        """
        integration_credentials_list = await integration_credentials_dao.get_all(db)
        return integration_credentials_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateIntegrationCredentialsParam) -> None:
        """
        创建用户第三方应用凭证

        :param db: 数据库会话
        :param obj: 创建用户第三方应用凭证参数
        :return:
        """
        await integration_credentials_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateIntegrationCredentialsParam) -> int:
        """
        更新用户第三方应用凭证

        :param db: 数据库会话
        :param pk: 用户第三方应用凭证 ID
        :param obj: 更新用户第三方应用凭证参数
        :return:
        """
        count = await integration_credentials_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteIntegrationCredentialsParam) -> int:
        """
        删除用户第三方应用凭证

        :param db: 数据库会话
        :param obj: 用户第三方应用凭证 ID 列表
        :return:
        """
        count = await integration_credentials_dao.delete(db, obj.pks)
        return count


integration_credentials_service: IntegrationCredentialsService = IntegrationCredentialsService()
