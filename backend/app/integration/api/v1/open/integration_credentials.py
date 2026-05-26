"""用户第三方应用凭证 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.integration.schema.integration_credentials import GetIntegrationCredentialsDetail
from backend.app.integration.service.integration_credentials_service import integration_credentials_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取用户第三方应用凭证列表',
    dependencies=[DependsPagination],
    name='open_get_integration_credentials',
)
async def get_integration_credentials(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetIntegrationCredentialsDetail]]:
    page_data = await integration_credentials_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取用户第三方应用凭证详情',
    name='open_get_integration_credentials_detail',
)
async def get_integration_credentials_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
) -> ResponseSchemaModel[GetIntegrationCredentialsDetail]:
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    return response_base.success(data=integration_credentials)
