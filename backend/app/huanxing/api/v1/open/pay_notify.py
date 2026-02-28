"""Open API — 支付回调接口（微信/支付宝异步通知，无需认证）"""

import json

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from backend.app.huanxing.crud.crud_pay_app import pay_app_dao
from backend.app.huanxing.crud.crud_pay_channel import pay_channel_dao
from backend.app.huanxing.service.pay.gateway import get_pay_client
from backend.app.huanxing.service.pay.wechat_pay import WechatPayClient
from backend.app.huanxing.service.pay.alipay_pay import AlipayClient
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
    """微信支付 V3 异步通知"""
    try:
        body = await request.body()
        raw_data = body.decode('utf-8')
        log.info(f'微信支付回调: {raw_data[:500]}')

        # 获取微信客户端
        pay_app = await pay_app_dao.get_by_app_key(db, 'huanxing')
        if not pay_app:
            return PlainTextResponse('{"code":"FAIL","message":"应用未配置"}', status_code=500)
        
        channel = await pay_channel_dao.get_by_app_and_code(db, pay_app.id, 'wx_native')
        if not channel:
            return PlainTextResponse('{"code":"FAIL","message":"渠道未配置"}', status_code=500)

        client = await get_pay_client(db, channel)
        if not isinstance(client, WechatPayClient):
            return PlainTextResponse('{"code":"FAIL","message":"客户端类型错误"}', status_code=500)

        # 验签 + 解密
        headers = {
            'Wechatpay-Timestamp': request.headers.get('Wechatpay-Timestamp', ''),
            'Wechatpay-Nonce': request.headers.get('Wechatpay-Nonce', ''),
            'Wechatpay-Signature': request.headers.get('Wechatpay-Signature', ''),
            'Wechatpay-Serial': request.headers.get('Wechatpay-Serial', ''),
        }
        
        notify_data = client.verify_and_decrypt_callback(headers, raw_data)
        log.info(f'微信回调解密数据: {notify_data}')

        # 提取关键字段
        trade_state = notify_data.get('trade_state')
        if trade_state == 'SUCCESS':
            order_no = notify_data['out_trade_no']
            channel_order_no = notify_data['transaction_id']
            pay_amount = notify_data['amount']['total']
            channel_user_id = notify_data.get('payer', {}).get('openid')

            await pay_order_service.handle_pay_notify(
                db=db,
                order_no=order_no,
                channel_order_no=channel_order_no,
                pay_amount=pay_amount,
                channel_code='wx_native',
                channel_user_id=channel_user_id,
                raw_data=raw_data,
            )

        return PlainTextResponse('{"code":"SUCCESS","message":"成功"}', status_code=200)
    except Exception as e:
        log.error(f'微信支付回调异常: {e}')
        return PlainTextResponse(f'{{"code":"FAIL","message":"{str(e)[:100]}"}}', status_code=500)


@router.post(
    '/pay/notify/alipay',
    summary='支付宝支付回调',
    response_class=PlainTextResponse,
)
async def alipay_pay_notify(request: Request, db: CurrentSessionTransaction) -> PlainTextResponse:
    """支付宝异步通知"""
    try:
        form_data = await request.form()
        data = dict(form_data)
        raw_data = json.dumps(data, ensure_ascii=False)
        log.info(f'支付宝回调: {raw_data[:500]}')

        # 获取支付宝客户端
        pay_app = await pay_app_dao.get_by_app_key(db, 'huanxing')
        if not pay_app:
            return PlainTextResponse('fail', status_code=200)

        channel = await pay_channel_dao.get_by_app_and_code(db, pay_app.id, 'alipay_pc')
        if not channel:
            return PlainTextResponse('fail', status_code=200)

        client = await get_pay_client(db, channel)
        if not isinstance(client, AlipayClient):
            return PlainTextResponse('fail', status_code=200)

        # 验签
        verify_data = dict(data)  # 复制一份
        if not client.verify_callback(verify_data):
            log.error('支付宝回调验签失败')
            return PlainTextResponse('fail', status_code=200)

        # 处理支付通知
        trade_status = data.get('trade_status')
        if trade_status in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
            order_no = data['out_trade_no']
            channel_order_no = data['trade_no']
            # 支付宝金额是元，转分
            pay_amount = int(float(data['total_amount']) * 100)
            channel_user_id = data.get('buyer_id')

            await pay_order_service.handle_pay_notify(
                db=db,
                order_no=order_no,
                channel_order_no=channel_order_no,
                pay_amount=pay_amount,
                channel_code='alipay_pc',
                channel_user_id=channel_user_id,
                raw_data=raw_data,
            )

        return PlainTextResponse('success', status_code=200)
    except Exception as e:
        log.error(f'支付宝回调异常: {e}')
        return PlainTextResponse('fail', status_code=200)


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

        pay_app = await pay_app_dao.get_by_app_key(db, 'huanxing')
        channel = await pay_channel_dao.get_by_app_and_code(db, pay_app.id, 'wx_native') if pay_app else None
        
        if channel:
            client = await get_pay_client(db, channel)
            if isinstance(client, WechatPayClient):
                headers = {
                    'Wechatpay-Timestamp': request.headers.get('Wechatpay-Timestamp', ''),
                    'Wechatpay-Nonce': request.headers.get('Wechatpay-Nonce', ''),
                    'Wechatpay-Signature': request.headers.get('Wechatpay-Signature', ''),
                    'Wechatpay-Serial': request.headers.get('Wechatpay-Serial', ''),
                }
                notify_data = client.verify_and_decrypt_callback(headers, raw_data)
                
                change_type = notify_data.get('change_type')
                if change_type == 'ADD':
                    # 签约成功
                    contract_no = notify_data.get('out_contract_code')
                    channel_contract_id = notify_data.get('contract_id')
                    if contract_no and channel_contract_id:
                        await pay_contract_service.handle_sign_notify(
                            db=db,
                            contract_no=contract_no,
                            channel_contract_id=channel_contract_id,
                        )
                elif change_type == 'DELETE':
                    # 解约
                    contract_no = notify_data.get('out_contract_code')
                    if contract_no:
                        await pay_contract_service.handle_unsign_notify(db=db, contract_no=contract_no)

        return PlainTextResponse('{"code":"SUCCESS","message":"成功"}', status_code=200)
    except Exception as e:
        log.error(f'微信签约回调异常: {e}')
        return PlainTextResponse(f'{{"code":"FAIL","message":"{str(e)[:100]}"}}', status_code=500)


@router.post(
    '/pay/notify/alipay/contract',
    summary='支付宝签约/解约回调',
    response_class=PlainTextResponse,
)
async def alipay_contract_notify(request: Request, db: CurrentSessionTransaction) -> PlainTextResponse:
    """支付宝周期扣款签约/解约通知"""
    try:
        form_data = await request.form()
        data = dict(form_data)
        raw_data = json.dumps(data, ensure_ascii=False)
        log.info(f'支付宝签约回调: {raw_data[:500]}')

        pay_app = await pay_app_dao.get_by_app_key(db, 'huanxing')
        channel = await pay_channel_dao.get_by_app_and_code(db, pay_app.id, 'alipay_pc') if pay_app else None

        if channel:
            client = await get_pay_client(db, channel)
            if isinstance(client, AlipayClient):
                verify_data = dict(data)
                if not client.verify_callback(verify_data):
                    log.error('支付宝签约回调验签失败')
                    return PlainTextResponse('fail', status_code=200)

                status = data.get('status')
                if status == 'NORMAL':
                    # 签约成功
                    contract_no = data.get('external_agreement_no')
                    agreement_no = data.get('agreement_no')
                    if contract_no and agreement_no:
                        await pay_contract_service.handle_sign_notify(
                            db=db,
                            contract_no=contract_no,
                            channel_contract_id=agreement_no,
                        )
                elif status == 'UNSIGN':
                    # 解约
                    contract_no = data.get('external_agreement_no')
                    if contract_no:
                        await pay_contract_service.handle_unsign_notify(db=db, contract_no=contract_no)

        return PlainTextResponse('success', status_code=200)
    except Exception as e:
        log.error(f'支付宝签约回调异常: {e}')
        return PlainTextResponse('fail', status_code=200)


@router.post(
    '/pay/notify/internal',
    summary='内部模拟支付回调（开发调试用）',
)
async def internal_pay_notify(request: Request, db: CurrentSessionTransaction) -> dict:
    """
    内部调试接口 — 手动触发支付成功
    生产环境应通过配置关闭或加密鉴权
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
        raw_data=json.dumps(data, ensure_ascii=False),
    )

    return {'code': 0, 'msg': '处理成功' if result else '已处理过', 'data': {'new': result}}
