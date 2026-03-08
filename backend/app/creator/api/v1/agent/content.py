from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_content_stage import hx_creator_content_stage_dao
from backend.app.creator.schema.hx_creator_content import CreateHxCreatorContentParam, UpdateHxCreatorContentParam
from backend.app.creator.schema.hx_creator_content_stage import CreateHxCreatorContentStageParam
from backend.app.creator.service.hx_creator_content_service import hx_creator_content_service
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AgentCreateContentParam(BaseModel):
    """Agent 创建内容参数"""
    project_id: int | None = Field(None, description='项目ID（不传则使用活跃项目）')
    title: str | None = Field(None, description='内容标题')
    target_platforms: dict | None = Field(None, description='目标平台')
    pipeline_mode: str | None = Field('semi-auto', description='流水线模式')
    content_tracks: str | None = Field('article', description='创作轨道')
    viral_pattern_id: int | None = Field(None, description='爆款模式ID')
    meta_data: dict | None = Field(None, description='扩展信息')


class AgentUpdateContentParam(BaseModel):
    """Agent 更新内容参数"""
    title: str | None = Field(None, description='标题')
    status: str | None = Field(None, description='状态')
    target_platforms: dict | None = Field(None, description='目标平台')
    meta_data: dict | None = Field(None, description='扩展信息')


class AgentSaveStageParam(BaseModel):
    """Agent 保存阶段产出参数"""
    stage: str = Field(description='阶段：research/outline/first_draft/final_draft/cover/video_script')
    content_text: str | None = Field(None, description='产出内容文本')
    file_url: str | None = Field(None, description='产出文件URL')
    source_type: str | None = Field('ai_generated', description='来源')
    meta_data: dict | None = Field(None, description='扩展信息')


@router.post(
    '',
    summary='创建内容',
    dependencies=[DependsJwtAuth],
)
async def agent_create_content(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentCreateContentParam,
) -> ResponseModel:
    user_id = request.user.id

    project_id = obj.project_id
    if not project_id:
        active_project = await hx_creator_project_service.get_active_project(db=db, user_id=user_id)
        if not active_project:
            raise errors.RequestError(msg='请先创建项目或指定 project_id')
        project_id = active_project.id

    project = await hx_creator_project_service.get(db=db, pk=project_id)
    if project.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该项目')

    create_param = CreateHxCreatorContentParam(
        project_id=project_id,
        user_id=user_id,
        title=obj.title,
        status='idea',
        target_platforms=obj.target_platforms,
        pipeline_mode=obj.pipeline_mode,
        content_tracks=obj.content_tracks,
        viral_pattern_id=obj.viral_pattern_id,
        meta_data=obj.meta_data,
    )
    content = await hx_creator_content_service.create_return(db=db, obj=create_param)
    return response_base.success(data={
        'id': content.id,
        'title': content.title,
        'status': content.status,
    })


@router.get(
    '',
    summary='列出内容',
    dependencies=[DependsJwtAuth],
)
async def agent_list_contents(
    request: Request,
    db: CurrentSession,
    status: Annotated[str | None, Query(description='状态筛选')] = None,
    project_id: Annotated[int | None, Query(description='项目ID筛选')] = None,
    limit: Annotated[int, Query(description='返回条数', ge=1, le=100)] = 50,
) -> ResponseModel:
    user_id = request.user.id
    contents = await hx_creator_content_service.get_by_user(
        db=db, user_id=user_id, status=status, project_id=project_id, limit=limit
    )
    return response_base.success(data=[
        {
            'id': c.id,
            'project_id': c.project_id,
            'title': c.title,
            'status': c.status,
            'target_platforms': c.target_platforms,
            'content_tracks': c.content_tracks,
            'created_time': c.created_time,
            'updated_time': c.updated_time,
        }
        for c in contents
    ])


@router.get(
    '/{pk}',
    summary='获取内容详情（含阶段产出）',
    dependencies=[DependsJwtAuth],
)
async def agent_get_content(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='内容ID')],
) -> ResponseModel:
    user_id = request.user.id
    data = await hx_creator_content_service.get_with_stages(db=db, pk=pk, user_id=user_id)
    return response_base.success(data=data)


@router.put(
    '/{pk}',
    summary='更新内容',
    dependencies=[DependsJwtAuth],
)
async def agent_update_content(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='内容ID')],
    obj: AgentUpdateContentParam,
) -> ResponseModel:
    user_id = request.user.id
    content = await hx_creator_content_service.get(db=db, pk=pk)
    if content.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该内容')

    # 如果有状态更新，走状态流转校验
    if obj.status and obj.status != content.status:
        await hx_creator_content_service.update_status(db=db, pk=pk, user_id=user_id, new_status=obj.status)

    # 更新其他字段
    update_data = obj.model_dump(exclude_unset=True, exclude={'status'})
    if update_data:
        update_param = UpdateHxCreatorContentParam(
            project_id=content.project_id,
            user_id=user_id,
            title=update_data.get('title', content.title),
            status=obj.status or content.status,
            target_platforms=update_data.get('target_platforms', content.target_platforms),
            pipeline_mode=content.pipeline_mode,
            content_tracks=content.content_tracks,
            viral_pattern_id=content.viral_pattern_id,
            meta_data=update_data.get('meta_data', content.meta_data),
        )
        await hx_creator_content_service.update(db=db, pk=pk, obj=update_param)

    return response_base.success()


@router.post(
    '/{pk}/stages',
    summary='保存阶段产出',
    dependencies=[DependsJwtAuth],
)
async def agent_save_stage(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='内容ID')],
    obj: AgentSaveStageParam,
) -> ResponseModel:
    user_id = request.user.id
    content = await hx_creator_content_service.get(db=db, pk=pk)
    if content.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该内容')

    create_param = CreateHxCreatorContentStageParam(
        content_id=pk,
        user_id=user_id,
        stage=obj.stage,
        content_text=obj.content_text,
        file_url=obj.file_url,
        status='draft',
        version=1,
        source_type=obj.source_type,
        meta_data=obj.meta_data,
    )
    stage = await hx_creator_content_stage_dao.create_return(db, create_param)
    return response_base.success(data={
        'id': stage.id,
        'stage': stage.stage,
        'content_id': pk,
    })
