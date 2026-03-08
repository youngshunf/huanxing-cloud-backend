from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorMedia
from backend.app.creator.schema.hx_creator_media import CreateHxCreatorMediaParam, UpdateHxCreatorMediaParam


class CRUDHxCreatorMedia(CRUDPlus[HxCreatorMedia]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorMedia | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorMedia]:
        return await self.select_models(db)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        media_type: str | None = None,
        keyword: str | None = None,
        limit: int = 50,
    ) -> Sequence[HxCreatorMedia]:
        """搜索用户的素材"""
        stmt = select(self.model).where(self.model.user_id == user_id)
        if media_type:
            stmt = stmt.where(self.model.type == media_type)
        if keyword:
            stmt = stmt.where(
                self.model.filename.ilike(f'%{keyword}%')
                | self.model.description.ilike(f'%{keyword}%')
            )
        stmt = stmt.order_by(self.model.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreateHxCreatorMediaParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorMediaParam) -> HxCreatorMedia:
        """创建并返回素材"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorMediaParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_media_dao: CRUDHxCreatorMedia = CRUDHxCreatorMedia(HxCreatorMedia)
