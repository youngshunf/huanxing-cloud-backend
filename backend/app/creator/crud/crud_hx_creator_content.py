from typing import Sequence

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorContent
from backend.app.creator.schema.hx_creator_content import CreateHxCreatorContentParam, UpdateHxCreatorContentParam


class CRUDHxCreatorContent(CRUDPlus[HxCreatorContent]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorContent | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorContent]:
        return await self.select_models(db)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        status: str | None = None,
        project_id: int | None = None,
        limit: int = 50,
    ) -> Sequence[HxCreatorContent]:
        """获取用户的内容列表，支持按状态和项目筛选"""
        stmt = select(self.model).where(self.model.user_id == user_id)
        if status:
            stmt = stmt.where(self.model.status == status)
        if project_id:
            stmt = stmt.where(self.model.project_id == project_id)
        stmt = stmt.order_by(self.model.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_project_id(self, db: AsyncSession, project_id: int) -> Sequence[HxCreatorContent]:
        """获取指定项目的所有内容"""
        return await self.select_models(db, project_id=project_id)

    async def update_status(self, db: AsyncSession, pk: int, status: str) -> int:
        """更新内容状态"""
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(status=status)
        )
        result = await db.execute(stmt)
        return result.rowcount  # type: ignore

    async def create(self, db: AsyncSession, obj: CreateHxCreatorContentParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorContentParam) -> HxCreatorContent:
        """创建并返回内容"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorContentParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_content_dao: CRUDHxCreatorContent = CRUDHxCreatorContent(HxCreatorContent)
