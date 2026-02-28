"""支付网关 — 统一调度微信/支付宝 SDK"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_pay_app import pay_app_dao
from backend.app.huanxing.crud.crud_pay_channel import pay_channel_dao
from backend.app.huanxing.model.pay_channel import PayChannel
from backend.app.huanxing.service.pay.wechat_pay import WechatPayClient
from backend.app.huanxing.service.pay.alipay_pay import AlipayClient
from backend.common.exception import errors
from backend.common.log import log


# 缓存客户端实例（按 channel_id 缓存，避免重复初始化）
_client_cache: dict[int, Any] = {}


async def _get_app_notify_url(db: AsyncSession, app_key: str = 'huanxing') -> str:
    """获取应用的回调 URL"""
    pay_app = await pay_app_dao.get_by_app_key(db, app_key)
    if not pay_app:
        raise errors.ServerError(msg='支付应用未配置')
    return pay_app.order_notify_url


def _build_client(channel: PayChannel, notify_url: str) -> WechatPayClient | AlipayClient:
    """根据渠道构建 SDK 客户端"""
    config = channel.config or {}
    code = channel.code

    if code.startswith('wx'):
        from backend.app.huanxing.service.pay.wechat_pay import create_wechat_client
        # 微信回调地址按渠道区分
        wx_notify_url = notify_url.replace('/internal', '/wechat')
        return create_wechat_client(config, wx_notify_url)
    elif code.startswith('alipay'):
        from backend.app.huanxing.service.pay.alipay_pay import create_alipay_client
        ali_notify_url = notify_url.replace('/internal', '/alipay')
        return create_alipay_client(config, ali_notify_url)
    else:
        raise errors.ServerError(msg=f'不支持的渠道: {code}')


async def get_pay_client(
    db: AsyncSession,
    channel: PayChannel,
    force_new: bool = False,
) -> WechatPayClient | AlipayClient:
    """获取支付客户端（带缓存）"""
    if not force_new and channel.id in _client_cache:
        return _client_cache[channel.id]

    notify_url = await _get_app_notify_url(db)
    client = _build_client(channel, notify_url)
    _client_cache[channel.id] = client
    return client


def clear_client_cache(channel_id: int | None = None):
    """清除客户端缓存（渠道配置更新后调用）"""
    if channel_id:
        _client_cache.pop(channel_id, None)
    else:
        _client_cache.clear()


async def create_payment(
    db: AsyncSession,
    channel: PayChannel,
    order_no: str,
    amount: int,
    subject: str,
    body: str = '',
    user_ip: str | None = None,
    contract_no: str | None = None,
    plan_id: str | None = None,
) -> dict[str, Any]:
    """
    统一下单接口
    
    :param channel: 支付渠道
    :param order_no: 商户订单号
    :param amount: 金额（分）
    :param subject: 标题
    :param body: 描述
    :param user_ip: 用户IP（H5支付需要）
    :param contract_no: 签约协议号（自动续费用）
    :param plan_id: 微信签约模板ID
    :return: {"qr_code_url": "...", "pay_url": "...", ...}
    """
    client = await get_pay_client(db, channel)
    code = channel.code

    try:
        if isinstance(client, WechatPayClient):
            if code == 'wx_native':
                result = client.create_native_order(order_no, amount, subject)
                return {'qr_code_url': result.get('code_url'), 'pay_url': None}
            elif code == 'wx_h5':
                result = client.create_h5_order(order_no, amount, subject, user_ip or '127.0.0.1')
                return {'qr_code_url': None, 'pay_url': result.get('h5_url')}
            elif code == 'wx_papay' and contract_no:
                result = client.create_sign_order(
                    order_no, amount, subject,
                    contract_no=contract_no,
                    plan_id=plan_id or '',
                )
                return {'qr_code_url': result.get('code_url'), 'pay_url': None, 'contract_no': contract_no}
            else:
                # 默认 Native
                result = client.create_native_order(order_no, amount, subject)
                return {'qr_code_url': result.get('code_url'), 'pay_url': None}

        elif isinstance(client, AlipayClient):
            # 金额转元（保留2位）
            amount_yuan = f'{amount / 100:.2f}'

            if code == 'alipay_pc':
                result = client.create_page_pay(order_no, amount_yuan, subject, body)
                return {'qr_code_url': None, 'pay_url': result.get('pay_url')}
            elif code == 'alipay_wap':
                result = client.create_wap_pay(order_no, amount_yuan, subject, body)
                return {'qr_code_url': None, 'pay_url': result.get('pay_url')}
            elif code == 'alipay_qr':
                result = client.create_qr_pay(order_no, amount_yuan, subject, body)
                return {'qr_code_url': result.get('qr_code'), 'pay_url': None}
            elif code == 'alipay_cycle' and contract_no:
                # 周期扣款签约支付
                result = client.create_agreement_pay(
                    order_no, amount_yuan, subject,
                    agreement_sign_params={
                        'personal_product_code': 'CYCLE_PAY_AUTH_P',
                        'sign_scene': 'INDUSTRY|DIGITAL_MEDIA',
                    },
                )
                return {'qr_code_url': None, 'pay_url': result.get('pay_url'), 'contract_no': contract_no}
            else:
                # 默认 PC 网页支付
                result = client.create_page_pay(order_no, amount_yuan, subject, body)
                return {'qr_code_url': None, 'pay_url': result.get('pay_url')}
        else:
            raise errors.ServerError(msg=f'未知客户端类型: {type(client)}')

    except errors.BaseError:
        raise
    except Exception as e:
        log.error(f'支付下单异常: channel={code}, order={order_no}, error={e}')
        raise errors.ServerError(msg=f'支付下单失败: {str(e)}')


async def query_payment(db: AsyncSession, channel: PayChannel, order_no: str) -> dict[str, Any]:
    """主动查询订单状态"""
    client = await get_pay_client(db, channel)
    try:
        if isinstance(client, WechatPayClient):
            return client.query_order(order_no)
        elif isinstance(client, AlipayClient):
            return client.query_order(order_no)
        else:
            raise errors.ServerError(msg='未知客户端')
    except Exception as e:
        log.error(f'查询订单异常: {e}')
        raise errors.ServerError(msg=f'查询订单失败: {str(e)}')


async def close_payment(db: AsyncSession, channel: PayChannel, order_no: str) -> bool:
    """关闭订单"""
    client = await get_pay_client(db, channel)
    try:
        if isinstance(client, WechatPayClient):
            return client.close_order(order_no)
        elif isinstance(client, AlipayClient):
            return client.close_order(order_no)
        return False
    except Exception as e:
        log.error(f'关闭订单异常: {e}')
        return False
