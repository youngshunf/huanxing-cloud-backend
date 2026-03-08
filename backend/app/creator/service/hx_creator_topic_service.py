from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_content import hx_creator_content_dao
from backend.app.creator.crud.crud_hx_creator_topic import hx_creator_topic_dao
from backend.app.creator.model import HxCreatorTopic
from backend.app.creator.schema.hx_creator_content import CreateHxCreatorContentParam
from backend.app.creator.schema.hx_creator_topic import CreateHxCreatorTopicParam, DeleteHxCreatorTopicParam, UpdateHxCreatorTopicParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorTopicService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorTopic:
        hx_creator_topic = await hx_creator_topic_dao.get(db, pk)
        if not hx_creator_topic:
            raise errors.NotFoundError(msg='选题推荐不存在')
        return hx_creator_topic

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        hx_creator_topic_select = await hx_creator_topic_dao.get_select()
        return await paging_data(db, hx_creator_topic_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorTopic]:
        return await hx_creator_topic_dao.get_all(db)

    @staticmethod
    async def get_by_user(
        *,
        db: AsyncSession,
        user_id: int,
        project_id: int | None = None,
        status: int | None = None,
        limit: int = 20,
    ) -> Sequence[HxCreatorTopic]:
        """获取用户的选题推荐列表"""
        return await hx_creator_topic_dao.get_by_user_id(
            db, user_id, project_id=project_id, status=status, limit=limit
        )

    @staticmethod
    async def adopt_topic(*, db: AsyncSession, pk: int, user_id: int) -> dict:
        """
        采纳选题：自动创建内容 + 更新选题状态

        :return: 新创建的内容信息
        """
        topic = await hx_creator_topic_dao.get(db, pk)
        if not topic:
            raise errors.NotFoundError(msg='选题不存在')
        if topic.user_id != user_id:
            raise errors.ForbiddenError(msg='无权操作该选题')
        if topic.status != 0:
            raise errors.RequestError(msg='该选题已被处理')

        # 创建内容
        content_obj = CreateHxCreatorContentParam(
            project_id=topic.project_id,
            user_id=user_id,
            title=topic.title,
            status='idea',
            target_platforms=None,
            pipeline_mode='semi-auto',
        )
        content = await hx_creator_content_dao.create_return(db, content_obj)

        # 更新选题状态
        await hx_creator_topic_dao.adopt(db, pk, content.id)

        return {
            'topic_id': topic.id,
            'content_id': content.id,
            'title': topic.title,
        }

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorTopicParam) -> None:
        await hx_creator_topic_dao.create(db, obj)

    @staticmethod
    async def create_return(*, db: AsyncSession, obj: CreateHxCreatorTopicParam) -> HxCreatorTopic:
        """创建并返回选题"""
        return await hx_creator_topic_dao.create_return(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorTopicParam) -> int:
        return await hx_creator_topic_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorTopicParam) -> int:
        return await hx_creator_topic_dao.delete(db, obj.pks)


hx_creator_topic_service: HxCreatorTopicService = HxCreatorTopicService()
