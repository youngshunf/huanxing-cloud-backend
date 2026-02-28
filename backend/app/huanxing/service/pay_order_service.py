"""支付订单核心 Service — 创建订单、回调处理、状态查询"""

import secrets
import time
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_pay_app import pay_app_dao
from backend.app.huanxing.crud.crud_pay_channel import pay_channel_dao
from backend.app.huanxing.crud.crud_pay_contract import pay_contract_dao
from backend.app.huanxing.crud.crud_pay_notify_log import pay_notify_log_dao
from backend.app.huanxing.crud.crud_pay_order import pay_order_dao
from backend.app.huanxing.model.pay_order import PayOrder
from backend.app.huanxing.schema.pay_order import (
    CreatePayOrderParam,
    CreatePayOrderResponse,
    PayOrderStatusResponse,
)
from backend.common.exception import errors
from backend.common.log import log
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone

# 订单过期时间（分钟）
ORDER_EXPIRE_MINUTES = 30

# 套餐价格表（分）— 后续可从数据库读取
TIER_PRICES = {
    'star_glow': {'monthly': 4900, 'yearly': 47000},
    'star_shine': {'monthly': 9900, 'yearly': 95000},
    'star_glory': {'monthly': 29900, 'yearly': 287000},
}

# 套餐显示名称
TIER_NAMES = {
    'star_glow': '星芒',
    'star_shine': '星辰',
    'star_glory': '星耀',
}


def _generate_order_no() -> str:
    """生成商户订单号: HX + 时间戳（毫秒） + 4位随机数"""
    ts = int(time.time() * 1000)
    rand = secrets.randbelow(10000)
    return f'HX{ts}{rand:04d}'


def _generate_contract_no() -> str:
    """生成签约协议号: CT + 时间戳 + 4位随机数"""
    ts = int(time.time() * 1000)
    rand = secrets.randbelow(10000)
    return f'CT{ts}{rand:04d}'


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
        """创建支付订单（用户端核心接口）"""

        # 1. 校验套餐
        if obj.tier not in TIER_PRICES:
            raise errors.RequestError(msg=f'无效的套餐: {obj.tier}')
        if obj.billing_cycle not in ('monthly', 'yearly'):
            raise errors.RequestError(msg=f'无效的计费周期: {obj.billing_cycle}')

        # 2. 查找默认支付应用
        pay_app = await pay_app_dao.get_by_app_key(db, 'huanxing')
        if not pay_app:
            raise errors.ServerError(msg='支付应用未配置')

        # 3. 查找支付渠道
        channel = await pay_channel_dao.get_by_app_and_code(db, pay_app.id, obj.channel_code)
        if not channel or channel.status != 1:
            raise errors.RequestError(msg=f'支付渠道 {obj.channel_code} 不可用')

        # 4. 计算金额
        price_info = TIER_PRICES[obj.tier]
        pay_amount = price_info[obj.billing_cycle]
        tier_name = TIER_NAMES[obj.tier]
        cycle_name = '月付' if obj.billing_cycle == 'monthly' else '年付'

        # 5. 生成订单号
        order_no = _generate_order_no()
        now = timezone.now()
        expire_time = now + timedelta(minutes=ORDER_EXPIRE_MINUTES)

        # 6. 创建订单
        order_dict = {
            'order_no': order_no,
            'user_id': user_id,
            'app_id': pay_app.id,
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

        # 7. 如果需要自动续费，创建签约记录
        contract_no = None
        if obj.auto_renew:
            contract_no = _generate_contract_no()
            contract_dict = {
                'user_id': user_id,
                'app_id': pay_app.id,
                'channel_code': channel.code,
                'contract_no': contract_no,
                'tier': obj.tier,
                'billing_cycle': obj.billing_cycle,
                'deduct_amount': pay_amount,
                'status': 0,  # 签约中
            }
            await pay_contract_dao.create(db, contract_dict)

        # 8. 调用支付 SDK 创建支付
        from backend.app.huanxing.service.pay.gateway import create_payment

        try:
            pay_result = await create_payment(
                db=db,
                channel=channel,
                order_no=order_no,
                amount=pay_amount,
                subject=f'唤星AI-{tier_name}会员-{cycle_name}',
                body=f'{tier_name}（{cycle_name}）订阅',
                user_ip=user_ip,
                contract_no=contract_no,
            )
            qr_code_url = pay_result.get('qr_code_url')
            pay_url = pay_result.get('pay_url')
        except Exception as e:
            # SDK 调用失败时回退到 mock 模式（渠道配置不完整时）
            log.warning(f'SDK 下单失败（回退mock）: {e}')
            qr_code_url = None
            pay_url = None
            if channel.code.startswith('wx'):
                qr_code_url = f'weixin://wxpay/bizpayurl?pr=mock_{order_no}'
            elif channel.code.startswith('alipay'):
                pay_url = f'https://openapi.alipay.com/gateway.do?mock=true&order_no={order_no}'

        return CreatePayOrderResponse(
            order_no=order_no,
            pay_amount=pay_amount,
            channel_code=channel.code,
            qr_code_url=qr_code_url,
            pay_url=pay_url,
            contract_no=contract_no,
            expire_time=expire_time,
        )

    @staticmethod
    async def cancel_order(*, db: AsyncSession, order_no: str, user_id: int) -> None:
        """用户取消订单"""
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
        """
        支付成功回调处理 — 幂等！
        
        :return: True=处理成功 False=已处理过
        """
        # 1. 记录回调日志
        await pay_notify_log_dao.create(db, {
            'notify_type': 'pay',
            'order_no': order_no,
            'channel_code': channel_code,
            'notify_data': raw_data,
            'status': 0,
        })

        # 2. 查订单（加锁防并发）
        order = await pay_order_dao.get_by_order_no_for_update(db, order_no)
        if not order:
            raise errors.NotFoundError(msg=f'订单 {order_no} 不存在')

        # 3. 幂等检查
        if order.status == 1:
            return False  # 已处理过

        # 4. 金额校验
        if order.pay_amount != pay_amount:
            raise errors.RequestError(msg=f'金额不一致: 订单 {order.pay_amount} vs 回调 {pay_amount}')

        # 5. 更新订单状态
        now = timezone.now()
        await pay_order_dao.update_status(
            db,
            order_no=order_no,
            status=1,
            channel_order_no=channel_order_no,
            channel_user_id=channel_user_id,
            success_time=now,
        )

        # 6. TODO: 业务处理 — 升级订阅 + 发放积分
        # 需要调用 user_tier 模块的 subscription_service
        # await subscription_service.upgrade(...)
        # await credit_service.grant_monthly(...)

        return True

    @staticmethod
    async def expire_timeout_orders(*, db: AsyncSession) -> int:
        """清理超时未支付订单（定时任务调用）"""
        return await pay_order_dao.expire_timeout_orders(db)


pay_order_service: PayOrderService = PayOrderService()
