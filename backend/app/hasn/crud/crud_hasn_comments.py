from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnComments
from backend.app.hasn.schema.hasn_comments import CreateHasnCommentsParam, UpdateHasnCommentsParam


class CRUDHasnComments(CRUDPlus[HasnComments]):
    async def get(self, db: AsyncSession, pk: int) -> HasnComments | None:
        """
        获取社区评论

        :param db: 数据库会话
        :param pk: 社区评论 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取社区评论列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnComments]:
        """
        获取所有社区评论

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnCommentsParam) -> None:
        """
        创建社区评论

        :param db: 数据库会话
        :param obj: 创建社区评论参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnCommentsParam) -> int:
        """
        更新社区评论

        :param db: 数据库会话
        :param pk: 社区评论 ID
        :param obj: 更新 社区评论参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除社区评论

        :param db: 数据库会话
        :param pks: 社区评论 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_comments_dao: CRUDHasnComments = CRUDHasnComments(HasnComments)
