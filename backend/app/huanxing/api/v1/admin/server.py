from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.huanxing.schema.huanxing_server import (
    CreateHuanxingServerParam,
    DashboardResponse,
    DeleteHuanxingServerParam,
    GetHuanxingServerDetail,
    HeartbeatParam,
    HeartbeatResponse,
    ServerStatsResponse,
    UpdateHuanxingServerParam,
)
from backend.app.huanxing.schema.huanxing_user import GetHuanxingUserDetail
from backend.app.huanxing.service.huanxing_server_service import huanxing_server_service
from backend.app.huanxing.service.huanxing_user_service import huanxing_user_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取唤星服务器详情', dependencies=[DependsJwtAuth])
async def get_huanxing_server(
    db: CurrentSession, pk: Annotated[int, Path(description='唤星服务器 ID')]
) -> ResponseSchemaModel[GetHuanxingServerDetail]:
    huanxing_server = await huanxing_server_service.get(db=db, pk=pk)
    return response_base.success(data=huanxing_server)


@router.get(
    '',
    summary='分页获取所有唤星服务器',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_huanxing_servers_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHuanxingServerDetail]]:
    page_data = await huanxing_server_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建唤星服务器',
    dependencies=[
        Depends(RequestPermission('huanxing:server:add')),
        DependsRBAC,
    ],
)
async def create_huanxing_server(db: CurrentSessionTransaction, obj: CreateHuanxingServerParam) -> ResponseModel:
    await huanxing_server_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新唤星服务器',
    dependencies=[
        Depends(RequestPermission('huanxing:server:edit')),
        DependsRBAC,
    ],
)
async def update_huanxing_server(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='唤星服务器 ID')], obj: UpdateHuanxingServerParam
) -> ResponseModel:
    count = await huanxing_server_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除唤星服务器',
    dependencies=[
        Depends(RequestPermission('huanxing:server:del')),
        DependsRBAC,
    ],
)
async def delete_huanxing_servers(db: CurrentSessionTransaction, obj: DeleteHuanxingServerParam) -> ResponseModel:
    count = await huanxing_server_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


# ========== 新增接口 ==========


@router.post(
    '/{server_id}/heartbeat',
    summary='服务器心跳上报',
    description='guardian 定期调用，上报服务器状态（Gateway状态、用户数、CPU/内存等）',
    dependencies=[DependsJwtAuth],
)
async def server_heartbeat(
    db: CurrentSessionTransaction,
    server_id: Annotated[str, Path(description='服务器唯一标识（如 server-001）')],
    obj: HeartbeatParam,
) -> ResponseSchemaModel[HeartbeatResponse]:
    result = await huanxing_server_service.heartbeat(db=db, server_id=server_id, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{server_id}/users',
    summary='获取指定服务器的用户列表',
    description='按服务器筛选唤星用户，分页返回',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_server_users(
    db: CurrentSession,
    server_id: Annotated[str, Path(description='服务器唯一标识（如 server-001）')],
) -> ResponseSchemaModel[PageData[GetHuanxingUserDetail]]:
    page_data = await huanxing_user_service.get_list_by_server(db=db, server_id=server_id)
    return response_base.success(data=page_data)


@router.get(
    '/{server_id}/stats',
    summary='获取指定服务器的统计数据',
    description='返回服务器的用户数、活跃数、按模板分布等统计信息',
    dependencies=[DependsJwtAuth],
)
async def get_server_stats(
    db: CurrentSession,
    server_id: Annotated[str, Path(description='服务器唯一标识（如 server-001）')],
) -> ResponseSchemaModel[ServerStatsResponse]:
    stats = await huanxing_server_service.get_server_stats(db=db, server_id=server_id)
    return response_base.success(data=stats)
