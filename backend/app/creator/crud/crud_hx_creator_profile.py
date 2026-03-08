from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorProfile
from backend.app.creator.schema.hx_creator_profile import CreateHxCreatorProfileParam, UpdateHxCreatorProfileParam


class CRUDHxCreatorProfile(CRUDPlus[HxCreatorProfile]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorProfile | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorProfile]:
        return await self.select_models(db)

    async def get_by_project_id(self, db: AsyncSession, project_id: int) -> HxCreatorProfile | None:
        """获取指定项目的画像"""
        return await self.select_model_by_column(db, project_id=project_id)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Sequence[HxCreatorProfile]:
        """获取用户的所有画像"""
        return await self.select_models(db, user_id=user_id)

    async def create(self, db: AsyncSession, obj: CreateHxCreatorProfileParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorProfileParam) -> HxCreatorProfile:
        """创建并返回画像"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorProfileParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_profile_dao: CRUDHxCreatorProfile = CRUDHxCreatorProfile(HxCreatorProfile)
