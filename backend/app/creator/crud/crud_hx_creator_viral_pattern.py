from typing import Sequence

from sqlalchemy import Select, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorViralPattern
from backend.app.creator.schema.hx_creator_viral_pattern import CreateHxCreatorViralPatternParam, UpdateHxCreatorViralPatternParam


class CRUDHxCreatorViralPattern(CRUDPlus[HxCreatorViralPattern]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorViralPattern | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorViralPattern]:
        return await self.select_models(db)

    async def search(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        category: str | None = None,
        platform: str | None = None,
        keyword: str | None = None,
        limit: int = 20,
    ) -> Sequence[HxCreatorViralPattern]:
        """搜索爆款模式（系统级 + 用户级）"""
        # 返回系统级（user_id is NULL）+ 用户自己的
        conditions = [self.model.user_id.is_(None)]
        if user_id:
            conditions.append(self.model.user_id == user_id)

        stmt = select(self.model).where(or_(*conditions))
        if category:
            stmt = stmt.where(self.model.category == category)
        if platform:
            stmt = stmt.where(self.model.platform == platform)
        if keyword:
            stmt = stmt.where(
                self.model.name.ilike(f'%{keyword}%')
                | self.model.description.ilike(f'%{keyword}%')
            )
        stmt = stmt.order_by(self.model.usage_count.desc().nullslast()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj: CreateHxCreatorViralPatternParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorViralPatternParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_viral_pattern_dao: CRUDHxCreatorViralPattern = CRUDHxCreatorViralPattern(HxCreatorViralPattern)
