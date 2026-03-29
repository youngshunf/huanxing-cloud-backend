"""HASN 客户端设备 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_clients import GetHasnClientsDetail
from backend.app.hasn.service.hasn_clients_service import hasn_clients_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 客户端设备列表',
    dependencies=[DependsPagination],
)
async def open_get_hasn_clientss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnClientsDetail]]:
    page_data = await hasn_clients_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 客户端设备详情',
)
async def open_get_hasn_clients(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 客户端设备 ID')],
) -> ResponseSchemaModel[GetHasnClientsDetail]:
    hasn_clients = await hasn_clients_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_clients)
