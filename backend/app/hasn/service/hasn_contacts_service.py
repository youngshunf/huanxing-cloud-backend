from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_contacts import hasn_contacts_dao
from backend.app.hasn.model import HasnContacts
from backend.app.hasn.schema.hasn_contacts import CreateHasnContactsParam, DeleteHasnContactsParam, UpdateHasnContactsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnContactsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnContacts:
        """
        获取HASN 联系人关系

        :param db: 数据库会话
        :param pk: HASN 联系人关系 ID
        :return:
        """
        hasn_contacts = await hasn_contacts_dao.get(db, pk)
        if not hasn_contacts:
            raise errors.NotFoundError(msg='HASN 联系人关系不存在')
        return hasn_contacts

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN 联系人关系列表

        :param db: 数据库会话
        :return:
        """
        hasn_contacts_select = await hasn_contacts_dao.get_select()
        return await paging_data(db, hasn_contacts_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnContacts]:
        """
        获取所有HASN 联系人关系

        :param db: 数据库会话
        :return:
        """
        hasn_contactss = await hasn_contacts_dao.get_all(db)
        return hasn_contactss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnContactsParam) -> None:
        """
        创建HASN 联系人关系

        :param db: 数据库会话
        :param obj: 创建HASN 联系人关系参数
        :return:
        """
        await hasn_contacts_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnContactsParam) -> int:
        """
        更新HASN 联系人关系

        :param db: 数据库会话
        :param pk: HASN 联系人关系 ID
        :param obj: 更新HASN 联系人关系参数
        :return:
        """
        count = await hasn_contacts_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnContactsParam) -> int:
        """
        删除HASN 联系人关系

        :param db: 数据库会话
        :param obj: HASN 联系人关系 ID 列表
        :return:
        """
        count = await hasn_contacts_dao.delete(db, obj.pks)
        return count


hasn_contacts_service: HasnContactsService = HasnContactsService()
