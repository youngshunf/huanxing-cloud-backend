from typing import Sequence

from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model import HuanxingUser
from backend.app.huanxing.schema.huanxing_user import CreateHuanxingUserParam, UpdateHuanxingUserParam


class CRUDHuanxingUser(CRUDPlus[HuanxingUser]):
    async def get(self, db: AsyncSession, pk: int) -> HuanxingUser | None:
        """
        获取唤星用户

        :param db: 数据库会话
        :param pk: 唤星用户 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取唤星用户列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_select_by_server(self, server_id: str) -> Select:
        """获取指定服务器的唤星用户列表查询表达式"""
        stmt = select(HuanxingUser).where(
            HuanxingUser.server_id == server_id
        ).order_by(HuanxingUser.id.desc())
        return stmt

    async def get_all(self, db: AsyncSession) -> Sequence[HuanxingUser]:
        """
        获取所有唤星用户

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def count_by_server(self, db: AsyncSession, server_id: str) -> int:
        """统计指定服务器的用户数"""
        result = await db.execute(
            select(func.count()).select_from(HuanxingUser).where(
                HuanxingUser.server_id == server_id
            )
        )
        return result.scalar() or 0

    async def count_active_by_server(self, db: AsyncSession, server_id: str) -> int:
        """统计指定服务器的活跃用户数（agent_status=1）"""
        result = await db.execute(
            select(func.count()).select_from(HuanxingUser).where(
                HuanxingUser.server_id == server_id,
                HuanxingUser.agent_status == 1,
            )
        )
        return result.scalar() or 0

    async def count_by_template(self, db: AsyncSession, server_id: str | None = None) -> list[dict]:
        """按模板统计用户数"""
        stmt = select(
            HuanxingUser.template,
            func.count().label('count')
        ).group_by(HuanxingUser.template)
        if server_id:
            stmt = stmt.where(HuanxingUser.server_id == server_id)
        result = await db.execute(stmt)
        return [{'template': row.template, 'count': row.count} for row in result.all()]

    async def count_total(self, db: AsyncSession) -> int:
        """统计所有用户总数"""
        result = await db.execute(
            select(func.count()).select_from(HuanxingUser)
        )
        return result.scalar() or 0

    async def count_total_active(self, db: AsyncSession) -> int:
        """统计所有活跃用户总数"""
        result = await db.execute(
            select(func.count()).select_from(HuanxingUser).where(
                HuanxingUser.agent_status == 1
            )
        )
        return result.scalar() or 0

    async def create(self, db: AsyncSession, obj: CreateHuanxingUserParam) -> None:
        """
        创建唤星用户

        :param db: 数据库会话
        :param obj: 创建唤星用户参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHuanxingUserParam) -> int:
        """
        更新唤星用户

        :param db: 数据库会话
        :param pk: 唤星用户 ID
        :param obj: 更新 唤星用户参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除唤星用户

        :param db: 数据库会话
        :param pks: 唤星用户 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


huanxing_user_dao: CRUDHuanxingUser = CRUDHuanxingUser(HuanxingUser)
