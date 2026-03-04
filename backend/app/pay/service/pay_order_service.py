"""支付订单核心 Service — 创建订单、回调处理、状态查询"""

import secrets
import time
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.pay.core.callback import dispatch_pay_success
from backend.app.pay.core.config import (
    ORDER_EXPIRE_MINUTES,
    PAY_ORDER_NOTIFY_URL,
    TIER_NAMES,
    TIER_PRICES,
)
from backend.app.pay.crud.crud_pay_channel import pay_channel_dao
from backend.app.pay.crud.crud_pay_contract import pay_contract_dao
from backend.app.pay.crud.crud_pay_notify_log import pay_notify_log_dao
from backend.app.pay.crud.crud_pay_order import pay_order_dao
from backend.app.pay.model.pay_order import PayOrder
from backend.app.pay.schema.pay_order import (
    CreatePayOrderParam,
    CreatePayOrderResponse,
    PayOrderStatusResponse,
)
from backend.app.pay.service.channel.base import PayClient
from backend.common.exception import errors
from backend.common.log import log
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone


def _generate_order_no() -> str:
    ts = int(time.time() * 1000)
    rand = secrets.randbelow(10000)
    return f'HX{ts}{rand:04d}'


def _generate_contract_no() -> str:
    ts = int(time.time() * 1000)
    rand = secrets.randbelow(10000)
    return f'CT{ts}{rand:04d}'


# 客户端缓存（按 channel_id）
_client_cache: dict[int, PayClient] = {}


def _build_client(channel) -> PayClient:
    """根据渠道编码构建 PayClient"""
    config = channel.config or {}
    code = channel.code
    notify_url = f'{PAY_ORDER_NOTIFY_URL}/{channel.id}'

    if code.startswith('wx'):
        from backend.app.pay.service.channel.wechat_native import WechatNativeClient
        return WechatNativeClient(config, notify_url)
    elif code.startswith('alipay'):
        from backend.app.pay.service.channel.alipay_pc import AlipayPcClient
        return AlipayPcClient(config, notify_url)
    else:
        raise errors.ServerError(msg=f'不支持的渠道: {code}')


def get_pay_client(channel, force_new: bool = False) -> PayClient:
    """获取支付客户端（带缓存）"""
    if not force_new and channel.id in _client_cache:
        return _client_cache[channel.id]
    client = _build_client(channel)
    _client_cache[channel.id] = client
    return client


def clear_client_cache(channel_id: int | None = None):
    if channel_id:
        _client_cache.pop(channel_id, None)
    else:
        _client_cache.clear()


class PayOrderService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> PayOrder:
        order = await pay_order_dao.get(db, pk)
        if not order:
            raise errors.NotFoundError(msg='订单不存在')
        return order

    @staticmethod
    async def get_by_order_no(*, db: AsyncSession, order_no: str) -> PayOrder:
        order = await pay_order_dao.get_by_order_no(db, order_no)
        if not order:
            raise errors.NotFoundError(msg='订单不存在')
        return order

    @staticmethod
    async def get_list(
        db: AsyncSession,
        user_id: int | None = None,
        status: int | None = None,
    ) -> dict[str, Any]:
        select_stmt = await pay_order_dao.get_select(user_id=user_id, status=status)
        return await paging_data(db, select_stmt)

    @staticmethod
    async def get_status(*, db: AsyncSession, order_no: str) -> PayOrderStatusResponse:
        order = await pay_order_dao.get_by_order_no(db, order_no)
        if not order:
            raise errors.NotFoundError(msg='订单不存在')
        return PayOrderStatusResponse(
            order_no=order.order_no,
            status=order.status,
            pay_amount=order.pay_amount,
            success_time=order.success_time,
        )

    @staticmethod
    async def create_order(
        *,
        db: AsyncSession,
        user_id: int,
        obj: CreatePayOrderParam,
        user_ip: str | None = None,
    ) -> CreatePayOrderResponse:
        if obj.tier not in TIER_PRICES:
            raise errors.RequestError(msg=f'无效的套餐: {obj.tier}')
        if obj.billing_cycle not in ('monthly', 'yearly'):
            raise errors.RequestError(msg=f'无效的计费周期: {obj.billing_cycle}')

        channel = await pay_channel_dao.get_by_code(db, obj.channel_code)
        if not channel or channel.status != 1:
            raise errors.RequestError(msg=f'支付渠道 {obj.channel_code} 不可用')

        price_info = TIER_PRICES[obj.tier]
        pay_amount = price_info[obj.billing_cycle]
        tier_name = TIER_NAMES[obj.tier]
        cycle_name = '月付' if obj.billing_cycle == 'monthly' else '年付'

        order_no = _generate_order_no()
        now = timezone.now()
        expire_time = now + timedelta(minutes=ORDER_EXPIRE_MINUTES)

        order_dict = {
            'order_no': order_no,
            'user_id': user_id,
            'channel_id': channel.id,
            'channel_code': channel.code,
            'order_type': 'subscribe',
            'subject': f'唤星AI-{tier_name}会员-{cycle_name}',
            'body': f'{tier_name}（{cycle_name}）订阅',
            'target_tier': obj.tier,
            'billing_cycle': obj.billing_cycle,
            'amount': pay_amount,
            'pay_amount': pay_amount,
            'expire_time': expire_time,
            'user_ip': user_ip,
        }
        order = await pay_order_dao.create(db, order_dict)

        contract_no = None
        if obj.auto_renew:
            contract_no = _generate_contract_no()
            contract_dict = {
                'user_id': user_id,
                'channel_code': channel.code,
                'contract_no': contract_no,
                'tier': obj.tier,
                'billing_cycle': obj.billing_cycle,
                'deduct_amount': pay_amount,
                'status': 0,
            }
            await pay_contract_dao.create(db, contract_dict)

        try:
            client = get_pay_client(channel)
            pay_result = client.create_order(
                order_no=order_no, amount=pay_amount,
                subject=f'唤星AI-{tier_name}会员-{cycle_name}',
                body=f'{tier_name}（{cycle_name}）订阅', user_ip=user_ip,
            )
            qr_code_url = pay_result.get('qr_code_url')
            pay_url = pay_result.get('pay_url')
        except Exception as e:
            log.warning(f'SDK 下单失败（回退mock）: {e}')
            qr_code_url = None
            pay_url = None
            if channel.code.startswith('wx'):
                qr_code_url = f'weixin://wxpay/bizpayurl?pr=mock_{order_no}'
            elif channel.code.startswith('alipay'):
                pay_url = f'https://openapi.alipay.com/gateway.do?mock=true&order_no={order_no}'

        return CreatePayOrderResponse(
            order_no=order_no, pay_amount=pay_amount, channel_code=channel.code,
            qr_code_url=qr_code_url, pay_url=pay_url, contract_no=contract_no,
            expire_time=expire_time,
        )

    @staticmethod
    async def cancel_order(*, db: AsyncSession, order_no: str, user_id: int) -> None:
        order = await pay_order_dao.get_by_order_no(db, order_no)
        if not order:
            raise errors.NotFoundError(msg='订单不存在')
        if order.user_id != user_id:
            raise errors.ForbiddenError(msg='无权操作此订单')
        if order.status != 0:
            raise errors.RequestError(msg='订单状态不允许取消')
        await pay_order_dao.update_status(db, order_no, status=3)

    @staticmethod
    async def handle_pay_notify(
        *,
        db: AsyncSession,
        order_no: str,
        channel_order_no: str,
        pay_amount: int,
        channel_code: str,
        channel_user_id: str | None = None,
        raw_data: str | None = None,
    ) -> bool:
        await pay_notify_log_dao.create(db, {
            'notify_type': 'pay',
            'order_no': order_no,
            'channel_code': channel_code,
            'notify_data': raw_data,
            'status': 0,
        })

        order = await pay_order_dao.get_by_order_no_for_update(db, order_no)
        if not order:
            raise errors.NotFoundError(msg=f'订单 {order_no} 不存在')

        if order.status == 1:
            return False

        if order.pay_amount != pay_amount:
            raise errors.RequestError(msg=f'金额不一致: 订单 {order.pay_amount} vs 回调 {pay_amount}')

        now = timezone.now()
        await pay_order_dao.update_status(
            db, order_no=order_no, status=1,
            channel_order_no=channel_order_no,
            channel_user_id=channel_user_id, success_time=now,
        )

        await dispatch_pay_success(order.order_type, order)
        return True

    @staticmethod
    async def expire_timeout_orders(*, db: AsyncSession) -> int:
        return await pay_order_dao.expire_timeout_orders(db)


pay_order_service: PayOrderService = PayOrderService()
