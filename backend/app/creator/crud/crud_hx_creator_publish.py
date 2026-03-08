from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorPublish
from backend.app.creator.schema.hx_creator_publish import CreateHxCreatorPublishParam, UpdateHxCreatorPublishParam


class CRUDHxCreatorPublish(CRUDPlus[HxCreatorPublish]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorPublish | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorPublish]:
        return await self.select_models(db)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        content_id: int | None = None,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> Sequence[HxCreatorPublish]:
        """获取用户的发布记录列表"""
        stmt = select(self.model).where(self.model.user_id == user_id)
        if content_id:
            stmt = stmt.where(self.model.content_id == content_id)
        if platform:
            stmt = stmt.where(self.model.platform == platform)
        if status:
            stmt = stmt.where(self.model.status == status)
        stmt = stmt.order_by(self.model.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_content_id(self, db: AsyncSession, content_id: int) -> Sequence[HxCreatorPublish]:
        """获取指定内容的所有发布记录"""
        return await self.select_models(db, content_id=content_id)

    async def create(self, db: AsyncSession, obj: CreateHxCreatorPublishParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorPublishParam) -> HxCreatorPublish:
        """创建并返回发布记录"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorPublishParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_publish_dao: CRUDHxCreatorPublish = CRUDHxCreatorPublish(HxCreatorPublish)
