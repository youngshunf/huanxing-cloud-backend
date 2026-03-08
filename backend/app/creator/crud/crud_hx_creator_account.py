from typing import Sequence

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorAccount
from backend.app.creator.schema.hx_creator_account import CreateHxCreatorAccountParam, UpdateHxCreatorAccountParam


class CRUDHxCreatorAccount(CRUDPlus[HxCreatorAccount]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorAccount | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorAccount]:
        return await self.select_models(db)

    async def get_by_user_id(self, db: AsyncSession, user_id: int, *, platform: str | None = None) -> Sequence[HxCreatorAccount]:
        """获取用户的平台账号列表"""
        stmt = select(self.model).where(self.model.user_id == user_id)
        if platform:
            stmt = stmt.where(self.model.platform == platform)
        stmt = stmt.order_by(self.model.id.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_project_id(self, db: AsyncSession, project_id: int) -> Sequence[HxCreatorAccount]:
        """获取指定项目的所有平台账号"""
        return await self.select_models(db, project_id=project_id)

    async def create(self, db: AsyncSession, obj: CreateHxCreatorAccountParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorAccountParam) -> HxCreatorAccount:
        """创建并返回平台账号"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorAccountParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_account_dao: CRUDHxCreatorAccount = CRUDHxCreatorAccount(HxCreatorAccount)
