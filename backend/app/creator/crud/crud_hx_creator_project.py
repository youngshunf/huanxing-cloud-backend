from typing import Sequence

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorProject
from backend.app.creator.schema.hx_creator_project import CreateHxCreatorProjectParam, UpdateHxCreatorProjectParam


class CRUDHxCreatorProject(CRUDPlus[HxCreatorProject]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorProject | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorProject]:
        return await self.select_models(db)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Sequence[HxCreatorProject]:
        """获取用户的所有项目"""
        return await self.select_models(db, user_id=user_id)

    async def get_active_project(self, db: AsyncSession, user_id: int) -> HxCreatorProject | None:
        """获取用户当前活跃项目"""
        return await self.select_model_by_column(db, user_id=user_id, is_active=True)

    async def deactivate_all(self, db: AsyncSession, user_id: int) -> int:
        """取消用户所有项目的活跃状态"""
        stmt = (
            update(self.model)
            .where(self.model.user_id == user_id, self.model.is_active == True)  # noqa: E712
            .values(is_active=False)
        )
        result = await db.execute(stmt)
        return result.rowcount  # type: ignore

    async def activate(self, db: AsyncSession, pk: int) -> int:
        """激活指定项目"""
        stmt = (
            update(self.model)
            .where(self.model.id == pk)
            .values(is_active=True)
        )
        result = await db.execute(stmt)
        return result.rowcount  # type: ignore

    async def create(self, db: AsyncSession, obj: CreateHxCreatorProjectParam) -> None:
        await self.create_model(db, obj)

    async def create_return(self, db: AsyncSession, obj: CreateHxCreatorProjectParam) -> HxCreatorProject:
        """创建并返回创作项目"""
        return await self.create_model(db, obj, commit=True)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorProjectParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_project_dao: CRUDHxCreatorProject = CRUDHxCreatorProject(HxCreatorProject)
