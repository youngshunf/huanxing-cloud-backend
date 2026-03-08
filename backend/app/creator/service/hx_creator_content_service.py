from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_content import hx_creator_content_dao
from backend.app.creator.crud.crud_hx_creator_content_stage import hx_creator_content_stage_dao
from backend.app.creator.model import HxCreatorContent
from backend.app.creator.schema.hx_creator_content import CreateHxCreatorContentParam, DeleteHxCreatorContentParam, UpdateHxCreatorContentParam
from backend.common.exception import errors
from backend.common.pagination import paging_data

# 合法的状态流转映射
VALID_STATUS_TRANSITIONS: dict[str, list[str]] = {
    'idea': ['researching', 'drafting', 'archived'],
    'researching': ['drafting', 'idea', 'archived'],
    'drafting': ['reviewing', 'researching', 'archived'],
    'reviewing': ['ready', 'drafting', 'archived'],
    'ready': ['published', 'reviewing', 'archived'],
    'published': ['analyzing', 'completed'],
    'analyzing': ['completed'],
    'completed': [],
    'archived': ['idea'],
}


class HxCreatorContentService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorContent:
        hx_creator_content = await hx_creator_content_dao.get(db, pk)
        if not hx_creator_content:
            raise errors.NotFoundError(msg='内容不存在')
        return hx_creator_content

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        hx_creator_content_select = await hx_creator_content_dao.get_select()
        return await paging_data(db, hx_creator_content_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorContent]:
        return await hx_creator_content_dao.get_all(db)

    @staticmethod
    async def get_by_user(
        *,
        db: AsyncSession,
        user_id: int,
        status: str | None = None,
        project_id: int | None = None,
        limit: int = 50,
    ) -> Sequence[HxCreatorContent]:
        """获取用户的内容列表"""
        return await hx_creator_content_dao.get_by_user_id(
            db, user_id, status=status, project_id=project_id, limit=limit
        )

    @staticmethod
    async def get_with_stages(*, db: AsyncSession, pk: int, user_id: int) -> dict:
        """获取内容详情（含阶段产出）"""
        content = await hx_creator_content_dao.get(db, pk)
        if not content:
            raise errors.NotFoundError(msg='内容不存在')
        if content.user_id != user_id:
            raise errors.ForbiddenError(msg='无权访问该内容')
        stages = await hx_creator_content_stage_dao.get_by_content_id(db, pk)
        return {
            'id': content.id,
            'project_id': content.project_id,
            'title': content.title,
            'status': content.status,
            'target_platforms': content.target_platforms,
            'pipeline_mode': content.pipeline_mode,
            'content_tracks': content.content_tracks,
            'viral_pattern_id': content.viral_pattern_id,
            'meta_data': content.meta_data,
            'created_time': content.created_time,
            'updated_time': content.updated_time,
            'stages': [
                {
                    'id': s.id,
                    'stage': s.stage,
                    'content_text': s.content_text,
                    'file_url': s.file_url,
                    'status': s.status,
                    'version': s.version,
                    'source_type': s.source_type,
                    'created_time': s.created_time,
                }
                for s in stages
            ],
        }

    @staticmethod
    async def update_status(*, db: AsyncSession, pk: int, user_id: int, new_status: str) -> int:
        """更新内容状态（校验状态流转）"""
        content = await hx_creator_content_dao.get(db, pk)
        if not content:
            raise errors.NotFoundError(msg='内容不存在')
        if content.user_id != user_id:
            raise errors.ForbiddenError(msg='无权操作该内容')
        current_status = content.status
        valid_next = VALID_STATUS_TRANSITIONS.get(current_status, [])
        if new_status not in valid_next:
            raise errors.RequestError(
                msg=f'状态流转不合法: {current_status} → {new_status}，允许: {valid_next}'
            )
        return await hx_creator_content_dao.update_status(db, pk, new_status)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorContentParam) -> None:
        await hx_creator_content_dao.create(db, obj)

    @staticmethod
    async def create_return(*, db: AsyncSession, obj: CreateHxCreatorContentParam) -> HxCreatorContent:
        """创建并返回内容"""
        return await hx_creator_content_dao.create_return(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorContentParam) -> int:
        return await hx_creator_content_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorContentParam) -> int:
        return await hx_creator_content_dao.delete(db, obj.pks)


hx_creator_content_service: HxCreatorContentService = HxCreatorContentService()
