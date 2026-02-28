"""Open API — 支付回调接口（微信/支付宝异步通知，无需认证）"""

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from backend.app.huanxing.service.pay_contract_service import pay_contract_service
from backend.app.huanxing.service.pay_order_service import pay_order_service
from backend.common.log import log
from backend.database.db import CurrentSessionTransaction

router = APIRouter()


@router.post(
    '/pay/notify/wechat',
    summary='微信支付回调',
    response_class=PlainTextResponse,
)
async def wechat_pay_notify(request: Request, db: CurrentSessionTransaction) -> PlainTextResponse:
    """
    微信支付异步通知入口
    
    TODO: 接入微信 SDK 后实现:
    1. 验证签名（v3 平台证书验签）
    2. 解密 resource 字段
    3. 提取 out_trade_no + transaction_id + amount.total
    4. 调用 pay_order_service.handle_pay_notify()
    """
    try:
        body = await request.body()
        raw_data = body.decode('utf-8')
        log.info(f'微信支付回调: {raw_data[:500]}')

        # TODO: 真实签名验证 + 解密
        # 临时返回成功，防止微信重试
        # wechat_data = verify_and_decrypt(request.headers, raw_data)
        # order_no = wechat_data['out_trade_no']
        # channel_order_no = wechat_data['transaction_id']
        # pay_amount = wechat_data['amount']['total']
        #
        # await pay_order_service.handle_pay_notify(
        #     db=db,
        #     order_no=order_no,
        #     channel_order_no=channel_order_no,
        #     pay_amount=pay_amount,
        #     channel_code='wx_native',
        #     raw_data=raw_data,
        # )

        return PlainTextResponse('{"code":"SUCCESS","message":"成功"}', status_code=200)
    except Exception as e:
        log.error(f'微信支付回调异常: {e}')
        return PlainTextResponse('{"code":"FAIL","message":"处理失败"}', status_code=500)


@router.post(
    '/pay/notify/alipay',
    summary='支付宝支付回调',
    response_class=PlainTextResponse,
)
async def alipay_pay_notify(request: Request, db: CurrentSessionTransaction) -> PlainTextResponse:
    """
    支付宝异步通知入口
    
    TODO: 接入支付宝 SDK 后实现:
    1. 验证签名（alipay.trade.page.pay 回调）
    2. 提取 out_trade_no + trade_no + total_amount
    3. 校验 trade_status == 'TRADE_SUCCESS'
    4. 调用 pay_order_service.handle_pay_notify()
    """
    try:
        form_data = await request.form()
        raw_data = str(dict(form_data))
        log.info(f'支付宝回调: {raw_data[:500]}')

        # TODO: 真实签名验证
        # trade_status = form_data.get('trade_status')
        # if trade_status == 'TRADE_SUCCESS':
        #     order_no = form_data['out_trade_no']
        #     channel_order_no = form_data['trade_no']
        #     pay_amount = int(float(form_data['total_amount']) * 100)
        #
        #     await pay_order_service.handle_pay_notify(
        #         db=db,
        #         order_no=order_no,
        #         channel_order_no=channel_order_no,
        #         pay_amount=pay_amount,
        #         channel_code='alipay_pc',
        #         raw_data=raw_data,
        #     )

        return PlainTextResponse('success', status_code=200)
    except Exception as e:
        log.error(f'支付宝回调异常: {e}')
        return PlainTextResponse('fail', status_code=500)


@router.post(
    '/pay/notify/wechat/contract',
    summary='微信签约/解约回调',
    response_class=PlainTextResponse,
)
async def wechat_contract_notify(request: Request, db: CurrentSessionTransaction) -> PlainTextResponse:
    """微信委托代扣签约/解约通知"""
    try:
        body = await request.body()
        raw_data = body.decode('utf-8')
        log.info(f'微信签约回调: {raw_data[:500]}')

        # TODO: 验签 + 解密 + 处理
        return PlainTextResponse('{"code":"SUCCESS","message":"成功"}', status_code=200)
    except Exception as e:
        log.error(f'微信签约回调异常: {e}')
        return PlainTextResponse('{"code":"FAIL","message":"处理失败"}', status_code=500)


@router.post(
    '/pay/notify/alipay/contract',
    summary='支付宝签约/解约回调',
    response_class=PlainTextResponse,
)
async def alipay_contract_notify(request: Request, db: CurrentSessionTransaction) -> PlainTextResponse:
    """支付宝周期扣款签约/解约通知"""
    try:
        form_data = await request.form()
        raw_data = str(dict(form_data))
        log.info(f'支付宝签约回调: {raw_data[:500]}')

        # TODO: 验签 + 处理
        return PlainTextResponse('success', status_code=200)
    except Exception as e:
        log.error(f'支付宝签约回调异常: {e}')
        return PlainTextResponse('fail', status_code=500)


@router.post(
    '/pay/notify/internal',
    summary='内部模拟支付回调（开发调试用）',
)
async def internal_pay_notify(request: Request, db: CurrentSessionTransaction) -> dict:
    """
    内部调试接口 — 手动触发支付成功
    生产环境应关闭或加密鉴权
    """
    data = await request.json()
    order_no = data.get('order_no')
    if not order_no:
        return {'code': 400, 'msg': 'order_no required'}

    result = await pay_order_service.handle_pay_notify(
        db=db,
        order_no=order_no,
        channel_order_no=f'MOCK_{order_no}',
        pay_amount=data.get('pay_amount', 0),
        channel_code=data.get('channel_code', 'mock'),
        raw_data=str(data),
    )

    return {'code': 0, 'msg': '处理成功' if result else '已处理过', 'data': {'new': result}}
