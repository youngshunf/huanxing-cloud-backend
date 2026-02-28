from typing import Sequence

from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model import HuanxingServer
from backend.app.huanxing.schema.huanxing_server import CreateHuanxingServerParam, UpdateHuanxingServerParam


class CRUDHuanxingServer(CRUDPlus[HuanxingServer]):
    async def get(self, db: AsyncSession, pk: int) -> HuanxingServer | None:
        """
        获取唤星服务器

        :param db: 数据库会话
        :param pk: 唤星服务器 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_by_server_id(self, db: AsyncSession, server_id: str) -> HuanxingServer | None:
        """
        通过 server_id 获取唤星服务器

        :param db: 数据库会话
        :param server_id: 服务器唯一标识
        :return:
        """
        result = await db.execute(
            select(HuanxingServer).where(HuanxingServer.server_id == server_id)
        )
        return result.scalars().first()

    async def get_select(self) -> Select:
        """获取唤星服务器列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HuanxingServer]:
        """
        获取所有唤星服务器

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHuanxingServerParam) -> None:
        """
        创建唤星服务器

        :param db: 数据库会话
        :param obj: 创建唤星服务器参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHuanxingServerParam) -> int:
        """
        更新唤星服务器

        :param db: 数据库会话
        :param pk: 唤星服务器 ID
        :param obj: 更新 唤星服务器参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除唤星服务器

        :param db: 数据库会话
        :param pks: 唤星服务器 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


huanxing_server_dao: CRUDHuanxingServer = CRUDHuanxingServer(HuanxingServer)
