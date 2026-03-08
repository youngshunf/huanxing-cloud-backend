from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.app.creator.schema.hx_creator_project import CreateHxCreatorProjectParam, UpdateHxCreatorProjectParam
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AgentCreateProjectParam(BaseModel):
    """Agent 创建项目参数"""
    name: str = Field(description='项目名称')
    platform: str = Field(description='主平台：xiaohongshu/douyin/wechat/weibo/bilibili')
    description: str | None = Field(None, description='项目描述')
    platforms: dict | None = Field(None, description='多平台JSON数组')
    avatar_url: str | None = Field(None, description='项目头像URL')


class AgentUpdateProjectParam(BaseModel):
    """Agent 更新项目参数"""
    name: str | None = Field(None, description='项目名称')
    description: str | None = Field(None, description='项目描述')
    platform: str | None = Field(None, description='主平台')
    platforms: dict | None = Field(None, description='多平台JSON数组')
    avatar_url: str | None = Field(None, description='项目头像URL')


@router.post(
    '',
    summary='创建项目',
    dependencies=[DependsJwtAuth],
)
async def agent_create_project(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentCreateProjectParam,
) -> ResponseModel:
    user_id = request.user.id
    create_param = CreateHxCreatorProjectParam(
        user_id=user_id,
        name=obj.name,
        platform=obj.platform,
        description=obj.description,
        platforms=obj.platforms,
        avatar_url=obj.avatar_url,
        is_active=False,
    )
    project = await hx_creator_project_service.create_return(db=db, obj=create_param)
    return response_base.success(data={
        'id': project.id,
        'name': project.name,
        'platform': project.platform,
        'is_active': project.is_active,
    })


@router.get(
    '',
    summary='列出项目',
    dependencies=[DependsJwtAuth],
)
async def agent_list_projects(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    user_id = request.user.id
    projects = await hx_creator_project_service.get_by_user(db=db, user_id=user_id)
    return response_base.success(data=[
        {
            'id': p.id,
            'name': p.name,
            'platform': p.platform,
            'platforms': p.platforms,
            'description': p.description,
            'is_active': p.is_active,
            'created_time': p.created_time,
        }
        for p in projects
    ])


@router.put(
    '/{pk}',
    summary='更新项目',
    dependencies=[DependsJwtAuth],
)
async def agent_update_project(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='项目ID')],
    obj: AgentUpdateProjectParam,
) -> ResponseModel:
    user_id = request.user.id
    project = await hx_creator_project_service.get(db=db, pk=pk)
    if project.user_id != user_id:
        from backend.common.exception import errors
        raise errors.ForbiddenError(msg='无权操作该项目')
    update_data = obj.model_dump(exclude_unset=True)
    if update_data:
        update_param = UpdateHxCreatorProjectParam(
            user_id=user_id,
            name=update_data.get('name', project.name),
            platform=update_data.get('platform', project.platform),
            description=update_data.get('description', project.description),
            platforms=update_data.get('platforms', project.platforms),
            avatar_url=update_data.get('avatar_url', project.avatar_url),
            is_active=project.is_active,
        )
        await hx_creator_project_service.update(db=db, pk=pk, obj=update_param)
    return response_base.success()


@router.put(
    '/{pk}/activate',
    summary='切换活跃项目',
    dependencies=[DependsJwtAuth],
)
async def agent_activate_project(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='项目ID')],
) -> ResponseModel:
    user_id = request.user.id
    await hx_creator_project_service.activate_project(db=db, user_id=user_id, project_id=pk)
    return response_base.success()
