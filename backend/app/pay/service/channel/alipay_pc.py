"""支付宝 PC 网页支付 — PayClient 实现"""

import json
from typing import Any

from backend.app.pay.service.channel.base import PayClient
from backend.common.log import log


class AlipayPcClient(PayClient):
    """支付宝 PC 网页支付客户端

    config JSONB 字段说明:
    {
        "app_id": "支付宝应用ID",
        "app_private_key": "应用私钥（PEM格式文本）",
        "alipay_public_key": "支付宝公钥（PEM格式文本）",
        "sign_type": "RSA2",
        "notify_url": "异步回调地址（可覆盖默认）",
        "return_url": "同步跳转地址",
        "debug": false
    }
    """

    def __init__(self, config: dict, notify_url: str):
        super().__init__(config, notify_url)
        self.return_url = config.get('return_url') or config.get('returnUrl', '')
        self._client = None
        # 兼容前端两种字段命名风格（camelCase 和 snake_case）
        self._app_id = config.get('appId') or config.get('app_id', '')
        self._private_key = config.get('privateKey') or config.get('app_private_key', '')
        self._public_key = config.get('alipayPublicKey') or config.get('alipay_public_key', '')
        self._sign_type = config.get('signType') or config.get('sign_type', 'RSA2')
        self._server_url = config.get('serverUrl') or config.get('server_url', '')
        self._is_debug = 'sandbox' in self._server_url if self._server_url else config.get('debug', False)

    @property
    def client(self):
        if self._client is None:
            from alipay import AliPay
            if not self._private_key:
                raise Exception('支付宝应用私钥未配置')
            self._client = AliPay(
                appid=self._app_id,
                app_notify_url=self.notify_url,
                app_private_key_string=self._private_key,
                alipay_public_key_string=self._public_key,
                sign_type=self._sign_type,
                debug=self._is_debug,
            )
        return self._client

    @property
    def gateway(self) -> str:
        if self._server_url:
            return self._server_url
        if self._is_debug:
            return 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
        return 'https://openapi.alipay.com/gateway.do'

    def create_order(
        self,
        order_no: str,
        amount: int,
        subject: str,
        body: str = '',
        user_ip: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        # 支付宝金额单位是元
        amount_yuan = f'{amount / 100:.2f}'
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            body=body,
            return_url=kwargs.get('return_url') or self.return_url,
        )
        pay_url = f'{self.gateway}?{order_string}'
        return {'qr_code_url': None, 'pay_url': pay_url}

    def query_order(self, order_no: str) -> dict[str, Any]:
        return self.client.api_alipay_trade_query(out_trade_no=order_no)

    def close_order(self, order_no: str) -> bool:
        result = self.client.api_alipay_trade_close(out_trade_no=order_no)
        return result.get('code') == '10000'

    def refund(
        self,
        order_no: str,
        refund_no: str,
        refund_amount: int,
        total_amount: int,
        reason: str = '',
        **kwargs: Any,
    ) -> dict[str, Any]:
        amount_yuan = f'{refund_amount / 100:.2f}'
        result = self.client.api_alipay_trade_refund(
            out_trade_no=order_no,
            refund_amount=amount_yuan,
            refund_reason=reason,
            out_request_no=refund_no,
        )
        if result.get('code') == '10000':
            return result
        raise Exception(f'支付宝退款失败: {result.get("sub_msg", result.get("msg"))}')

    def verify_callback(self, headers: dict, body: str | dict) -> dict[str, Any]:
        """验签支付宝回调"""
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = dict(body)
        verify_data = dict(data)
        signature = verify_data.pop('sign', '')
        verify_data.pop('sign_type', None)
        if self.client.verify(verify_data, signature):
            return data
        raise Exception('支付宝回调验签失败')
