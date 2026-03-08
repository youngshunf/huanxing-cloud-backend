from typing import Annotated

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_media import hx_creator_media_dao
from backend.app.creator.schema.hx_creator_media import CreateHxCreatorMediaParam
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AgentAddMediaParam(BaseModel):
    """Agent 添加素材参数"""
    project_id: int | None = Field(None, description='项目ID（不传则使用活跃项目）')
    type: str = Field(description='类型：image/video/audio/template')
    url: str = Field(description='文件URL')
    filename: str = Field(description='文件名')
    size: int | None = Field(None, description='文件大小')
    width: int | None = Field(None, description='宽度')
    height: int | None = Field(None, description='高度')
    duration: int | None = Field(None, description='时长（秒）')
    thumbnail_url: str | None = Field(None, description='缩略图URL')
    tags: dict | None = Field(None, description='标签')
    description: str | None = Field(None, description='描述')


@router.post(
    '',
    summary='添加素材',
    dependencies=[DependsJwtAuth],
)
async def agent_add_media(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentAddMediaParam,
) -> ResponseModel:
    user_id = request.user.id

    project_id = obj.project_id
    if not project_id:
        active_project = await hx_creator_project_service.get_active_project(db=db, user_id=user_id)
        if not active_project:
            raise errors.RequestError(msg='请先创建项目或指定 project_id')
        project_id = active_project.id

    create_param = CreateHxCreatorMediaParam(
        project_id=project_id,
        user_id=user_id,
        type=obj.type,
        url=obj.url,
        filename=obj.filename,
        size=obj.size,
        width=obj.width,
        height=obj.height,
        duration=obj.duration,
        thumbnail_url=obj.thumbnail_url,
        tags=obj.tags,
        description=obj.description,
    )
    media = await hx_creator_media_dao.create_return(db, create_param)
    return response_base.success(data={
        'id': media.id,
        'type': media.type,
        'filename': media.filename,
        'url': media.url,
    })


@router.get(
    '',
    summary='搜索素材',
    dependencies=[DependsJwtAuth],
)
async def agent_search_media(
    request: Request,
    db: CurrentSession,
    type: Annotated[str | None, Query(description='类型筛选')] = None,
    keyword: Annotated[str | None, Query(description='关键词搜索')] = None,
    limit: Annotated[int, Query(description='返回条数', ge=1, le=100)] = 50,
) -> ResponseModel:
    user_id = request.user.id
    media_list = await hx_creator_media_dao.get_by_user_id(
        db, user_id, media_type=type, keyword=keyword, limit=limit
    )
    return response_base.success(data=[
        {
            'id': m.id,
            'type': m.type,
            'url': m.url,
            'filename': m.filename,
            'size': m.size,
            'width': m.width,
            'height': m.height,
            'duration': m.duration,
            'thumbnail_url': m.thumbnail_url,
            'tags': m.tags,
            'description': m.description,
            'created_time': m.created_time,
        }
        for m in media_list
    ])
