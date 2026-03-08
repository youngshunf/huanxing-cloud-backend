from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_project import hx_creator_project_dao
from backend.app.creator.model import HxCreatorProject
from backend.app.creator.schema.hx_creator_project import CreateHxCreatorProjectParam, DeleteHxCreatorProjectParam, UpdateHxCreatorProjectParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorProjectService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorProject:
        hx_creator_project = await hx_creator_project_dao.get(db, pk)
        if not hx_creator_project:
            raise errors.NotFoundError(msg='创作项目不存在')
        return hx_creator_project

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        hx_creator_project_select = await hx_creator_project_dao.get_select()
        return await paging_data(db, hx_creator_project_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorProject]:
        return await hx_creator_project_dao.get_all(db)

    @staticmethod
    async def get_by_user(*, db: AsyncSession, user_id: int) -> Sequence[HxCreatorProject]:
        """获取用户的所有项目"""
        return await hx_creator_project_dao.get_by_user_id(db, user_id)

    @staticmethod
    async def get_active_project(*, db: AsyncSession, user_id: int) -> HxCreatorProject | None:
        """获取用户当前活跃项目"""
        return await hx_creator_project_dao.get_active_project(db, user_id)

    @staticmethod
    async def activate_project(*, db: AsyncSession, user_id: int, project_id: int) -> None:
        """切换活跃项目：先取消其他项目的活跃状态，再激活指定项目"""
        project = await hx_creator_project_dao.get(db, project_id)
        if not project:
            raise errors.NotFoundError(msg='项目不存在')
        if project.user_id != user_id:
            raise errors.ForbiddenError(msg='无权操作该项目')
        # 先取消所有活跃状态
        await hx_creator_project_dao.deactivate_all(db, user_id)
        # 再激活目标项目
        await hx_creator_project_dao.activate(db, project_id)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorProjectParam) -> None:
        await hx_creator_project_dao.create(db, obj)

    @staticmethod
    async def create_return(*, db: AsyncSession, obj: CreateHxCreatorProjectParam) -> HxCreatorProject:
        """创建并返回创作项目"""
        return await hx_creator_project_dao.create_return(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorProjectParam) -> int:
        return await hx_creator_project_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorProjectParam) -> int:
        return await hx_creator_project_dao.delete(db, obj.pks)


hx_creator_project_service: HxCreatorProjectService = HxCreatorProjectService()
