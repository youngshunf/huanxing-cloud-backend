from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_contact_requests import hasn_contact_requests_dao
from backend.app.hasn.model import HasnContactRequests
from backend.app.hasn.schema.hasn_contact_requests import (
    CreateHasnContactRequestsParam,
    DeleteHasnContactRequestsParam,
    UpdateHasnContactRequestsParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnContactRequestsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnContactRequests:
        """
        获取HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param pk: HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID
        :return:
        """
        hasn_contact_requests = await hasn_contact_requests_dao.get(db, pk)
        if not hasn_contact_requests:
            raise errors.NotFoundError(msg='HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）不存在')
        return hasn_contact_requests

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）列表

        :param db: 数据库会话
        :return:
        """
        hasn_contact_requests_select = await hasn_contact_requests_dao.get_select()
        return await paging_data(db, hasn_contact_requests_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnContactRequests]:
        """
        获取所有HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :return:
        """
        hasn_contact_requests_list = await hasn_contact_requests_dao.get_all(db)
        return hasn_contact_requests_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnContactRequestsParam) -> None:
        """
        创建HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param obj: 创建HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数
        :return:
        """
        await hasn_contact_requests_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnContactRequestsParam) -> int:
        """
        更新HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param pk: HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID
        :param obj: 更新HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数
        :return:
        """
        count = await hasn_contact_requests_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnContactRequestsParam) -> int:
        """
        删除HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param obj: HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID 列表
        :return:
        """
        count = await hasn_contact_requests_dao.delete(db, obj.pks)
        return count


hasn_contact_requests_service: HasnContactRequestsService = HasnContactRequestsService()
