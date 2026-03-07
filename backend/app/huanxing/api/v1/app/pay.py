"""App API — 用户端支付（创建订单 + 查询 + 签约管理）"""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.huanxing.schema.pay_channel import GetPayChannelSimple
from backend.app.huanxing.schema.pay_contract import GetPayContractUserView
from backend.app.huanxing.schema.pay_order import (
    CreatePayOrderParam,
    CreatePayOrderResponse,
    GetPayOrderDetail,
    PayOrderStatusResponse,
)
from backend.app.huanxing.service.pay_channel_service import pay_channel_service
from backend.app.huanxing.service.pay_contract_service import pay_contract_service
from backend.app.huanxing.service.pay_order_service import pay_order_service
from backend.app.huanxing.crud.crud_pay_app import pay_app_dao
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


# ============================================================
# 支付渠道（用户端展示，不含密钥）
# ============================================================

@router.get(
    '/channels',
    summary='获取可用支付渠道列表',
    dependencies=[DependsJwtAuth],
)
async def get_available_channels(
    db: CurrentSession,
) -> ResponseSchemaModel[list[GetPayChannelSimple]]:
    pay_app = await pay_app_dao.get_by_app_key(db, 'huanxing')
    if not pay_app:
        return response_base.success(data=[])
    channels = await pay_channel_service.get_active_channels(db=db, app_id=pay_app.id)
    simple_list = [
        GetPayChannelSimple(id=ch.id, code=ch.code, name=ch.name)
        for ch in channels
    ]
    return response_base.success(data=simple_list)


# ============================================================
# 订单
# ============================================================

@router.post(
    '/orders',
    summary='创建支付订单',
    dependencies=[DependsJwtAuth],
)
async def create_pay_order(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreatePayOrderParam,
) -> ResponseSchemaModel[CreatePayOrderResponse]:
    user_id = request.user.id
    user_ip = request.client.host if request.client else None
    result = await pay_order_service.create_order(
        db=db, user_id=user_id, obj=obj, user_ip=user_ip
    )
    return response_base.success(data=result)


@router.get(
    '/orders',
    summary='我的订单列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_orders(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetPayOrderDetail]]:
    user_id = request.user.id
    page_data = await pay_order_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=page_data)


@router.get(
    '/orders/{order_no}/status',
    summary='查询订单支付状态（轮询用）',
    dependencies=[DependsJwtAuth],
)
async def get_order_status(
    db: CurrentSession,
    order_no: Annotated[str, Path(description='商户订单号')],
) -> ResponseSchemaModel[PayOrderStatusResponse]:
    result = await pay_order_service.get_status(db=db, order_no=order_no)
    return response_base.success(data=result)


@router.post(
    '/orders/{order_no}/cancel',
    summary='取消订单',
    dependencies=[DependsJwtAuth],
)
async def cancel_order(
    request: Request,
    db: CurrentSessionTransaction,
    order_no: Annotated[str, Path(description='商户订单号')],
) -> ResponseModel:
    user_id = request.user.id
    await pay_order_service.cancel_order(db=db, order_no=order_no, user_id=user_id)
    return response_base.success()


# ============================================================
# 签约（自动续费）
# ============================================================

@router.get(
    '/contract',
    summary='获取我的签约状态',
    dependencies=[DependsJwtAuth],
)
async def get_my_contract(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[GetPayContractUserView]:
    user_id = request.user.id
    result = await pay_contract_service.get_user_contract(db=db, user_id=user_id)
    return response_base.success(data=result)


@router.post(
    '/contract/cancel',
    summary='取消自动续费',
    dependencies=[DependsJwtAuth],
)
async def cancel_auto_renew(
    request: Request,
    db: CurrentSessionTransaction,
) -> ResponseModel:
    user_id = request.user.id
    await pay_contract_service.cancel_contract(db=db, user_id=user_id)
    return response_base.success()
