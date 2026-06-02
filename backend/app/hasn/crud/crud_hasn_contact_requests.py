from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnContactRequests
from backend.app.hasn.schema.hasn_contact_requests import CreateHasnContactRequestsParam, UpdateHasnContactRequestsParam


class CRUDHasnContactRequests(CRUDPlus[HasnContactRequests]):
    async def get(self, db: AsyncSession, pk: int) -> HasnContactRequests | None:
        """
        获取HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param pk: HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnContactRequests]:
        """
        获取所有HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnContactRequestsParam) -> None:
        """
        创建HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param obj: 创建HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnContactRequestsParam) -> int:
        """
        更新HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param pk: HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID
        :param obj: 更新 HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）

        :param db: 数据库会话
        :param pks: HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_contact_requests_dao: CRUDHasnContactRequests = CRUDHasnContactRequests(HasnContactRequests)
