from typing import Sequence

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorTopic
from backend.app.creator.schema.hx_creator_topic import CreateHxCreatorTopicParam, UpdateHxCreatorTopicParam


class CRUDHxCreatorTopic(CRUDPlus[HxCreatorTopic]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorTopic | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorTopic]:
        return await self.select_models(db)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        project_id: int | None = None,
        status: int | None = None,
        limit: int = 20,
    ) -> Sequence[HxCreatorTopic]:
        """获取用户的选题推荐列表"""
        stmt = select(self.model).where(self.model.user_id == user_id)
        if project_id:
            stmt = stmt.where(self.model.project_id == project_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        stmt = stmt.order_by(self.model.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def adopt(self, db: AsyncSession, pk: int, content_id: int) -> int:
        """采纳选题，关联到新创建的内容"""
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(status=1, content_id=content_id)
        )
        result = await db.execute(stmt)
        return result.rowcount  # type: ignore

    async def skip(self, db: AsyncSession, pk: int) -> int:
        """跳过选题"""
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(status=2)
        )
        result = await db.execute(stmt)
        return result.rowcount  # type: ignore

    async def create(self, db: AsyncSession, obj: CreateHxCreatorTopicParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorTopicParam) -> HxCreatorTopic:
        """创建并返回选题"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorTopicParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_topic_dao: CRUDHxCreatorTopic = CRUDHxCreatorTopic(HxCreatorTopic)
