from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model.pay_channel import PayChannel
from backend.app.huanxing.schema.pay_channel import CreatePayChannelParam, UpdatePayChannelParam


class CRUDPayChannel(CRUDPlus[PayChannel]):
    async def get(self, db: AsyncSession, pk: int) -> PayChannel | None:
        return await self.select_model(db, pk)

    async def get_by_app_and_code(self, db: AsyncSession, app_id: int, code: str) -> PayChannel | None:
        result = await db.execute(
            select(PayChannel).where(PayChannel.app_id == app_id, PayChannel.code == code)
        )
        return result.scalars().first()

    async def get_select(self, app_id: int | None = None) -> Select:
        stmt = select(PayChannel)
        if app_id is not None:
            stmt = stmt.where(PayChannel.app_id == app_id)
        return stmt.order_by(PayChannel.id.desc())

    async def get_active_by_app(self, db: AsyncSession, app_id: int) -> Sequence[PayChannel]:
        """获取指定应用下所有启用的渠道"""
        result = await db.execute(
            select(PayChannel).where(PayChannel.app_id == app_id, PayChannel.status == 1)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreatePayChannelParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdatePayChannelParam) -> int:
        return await self.update_model(db, pk, obj)

    async def update_status(self, db: AsyncSession, pk: int, status: int) -> int:
        from sqlalchemy import update
        from backend.utils.timezone import timezone
        result = await db.execute(
            update(PayChannel).where(PayChannel.id == pk).values(status=status, updated_time=timezone.now())
        )
        return result.rowcount

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


pay_channel_dao: CRUDPayChannel = CRUDPayChannel(PayChannel)
