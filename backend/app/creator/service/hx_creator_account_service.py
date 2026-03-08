from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_account import hx_creator_account_dao
from backend.app.creator.model import HxCreatorAccount
from backend.app.creator.schema.hx_creator_account import CreateHxCreatorAccountParam, DeleteHxCreatorAccountParam, UpdateHxCreatorAccountParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorAccountService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorAccount:
        """
        获取平台账号

        :param db: 数据库会话
        :param pk: 平台账号 ID
        :return:
        """
        hx_creator_account = await hx_creator_account_dao.get(db, pk)
        if not hx_creator_account:
            raise errors.NotFoundError(msg='平台账号不存在')
        return hx_creator_account

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取平台账号列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_account_select = await hx_creator_account_dao.get_select()
        return await paging_data(db, hx_creator_account_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorAccount]:
        """
        获取所有平台账号

        :param db: 数据库会话
        :return:
        """
        hx_creator_accounts = await hx_creator_account_dao.get_all(db)
        return hx_creator_accounts

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorAccountParam) -> None:
        """
        创建平台账号

        :param db: 数据库会话
        :param obj: 创建平台账号参数
        :return:
        """
        await hx_creator_account_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorAccountParam) -> int:
        """
        更新平台账号

        :param db: 数据库会话
        :param pk: 平台账号 ID
        :param obj: 更新平台账号参数
        :return:
        """
        count = await hx_creator_account_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorAccountParam) -> int:
        """
        删除平台账号

        :param db: 数据库会话
        :param obj: 平台账号 ID 列表
        :return:
        """
        count = await hx_creator_account_dao.delete(db, obj.pks)
        return count


hx_creator_account_service: HxCreatorAccountService = HxCreatorAccountService()
