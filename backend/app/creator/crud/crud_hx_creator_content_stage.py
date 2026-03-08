from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorContentStage
from backend.app.creator.schema.hx_creator_content_stage import CreateHxCreatorContentStageParam, UpdateHxCreatorContentStageParam


class CRUDHxCreatorContentStage(CRUDPlus[HxCreatorContentStage]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorContentStage | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorContentStage]:
        return await self.select_models(db)

    async def get_by_content_id(self, db: AsyncSession, content_id: int) -> Sequence[HxCreatorContentStage]:
        """获取指定内容的所有阶段产出"""
        stmt = (
            select(self.model)
            .where(self.model.content_id == content_id)
            .order_by(self.model.created_time.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreateHxCreatorContentStageParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorContentStageParam) -> HxCreatorContentStage:
        """创建并返回阶段产出"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorContentStageParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_content_stage_dao: CRUDHxCreatorContentStage = CRUDHxCreatorContentStage(HxCreatorContentStage)
