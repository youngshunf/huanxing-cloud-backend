from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model.pay_app import PayApp
from backend.app.huanxing.schema.pay_app import CreatePayAppParam, UpdatePayAppParam


class CRUDPayApp(CRUDPlus[PayApp]):
    async def get(self, db: AsyncSession, pk: int) -> PayApp | None:
        return await self.select_model(db, pk)

    async def get_by_app_key(self, db: AsyncSession, app_key: str) -> PayApp | None:
        result = await db.execute(select(PayApp).where(PayApp.app_key == app_key))
        return result.scalars().first()

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[PayApp]:
        return await self.select_models(db)

    async def get_active(self, db: AsyncSession) -> Sequence[PayApp]:
        """获取所有启用的支付应用"""
        result = await db.execute(select(PayApp).where(PayApp.status == 1))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreatePayAppParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdatePayAppParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


pay_app_dao: CRUDPayApp = CRUDPayApp(PayApp)
