"""HASN 会话产物 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_session_artifacts import GetHasnSessionArtifactsDetail
from backend.app.hasn.service.hasn_session_artifacts_service import hasn_session_artifacts_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 会话产物列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_session_artifacts',
)
async def get_hasn_session_artifacts(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnSessionArtifactsDetail]]:
    page_data = await hasn_session_artifacts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 会话产物详情',
    name='open_get_hasn_session_artifacts_detail',
)
async def get_hasn_session_artifacts_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 会话产物 ID')],
) -> ResponseSchemaModel[GetHasnSessionArtifactsDetail]:
    hasn_session_artifacts = await hasn_session_artifacts_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_session_artifacts)
