"""支付宝 SDK 封装 — 从数据库读取配置"""

import json
import logging
import textwrap
from typing import Any

from backend.common.log import log

logger = logging.getLogger(__name__)


def _wrap_pem(key_string: str, key_type: str = 'PRIVATE') -> str:
    """把裸 base64 字符串包装为完整 PEM 格式

    支付宝开放平台复制出来的私钥/公钥是纯 base64 字符串（无 PEM 头尾），
    python-alipay-sdk 底层的 RSA.importKey() 要求完整 PEM 格式。

    密钥格式说明：
      - 支付宝私钥 = PKCS#8 → BEGIN PRIVATE KEY
      - 支付宝公钥 = SubjectPublicKeyInfo → BEGIN PUBLIC KEY
    """
    if not key_string or not key_string.strip():
        return key_string
    s = key_string.strip()
    if s.startswith('-----BEGIN'):
        return s
    raw = s.replace('\n', '').replace('\r', '').replace(' ', '')
    body = '\n'.join(textwrap.wrap(raw, 64))
    if key_type == 'PRIVATE':
        return f'-----BEGIN PRIVATE KEY-----\n{body}\n-----END PRIVATE KEY-----'
    else:
        return f'-----BEGIN PUBLIC KEY-----\n{body}\n-----END PUBLIC KEY-----'


class AlipayClient:
    """支付宝支付客户端

    config JSONB 字段说明（兼容 camelCase 和 snake_case）:
    {
        "appId" / "app_id": "支付宝应用ID",
        "privateKey" / "app_private_key": "应用私钥（裸base64或PEM均可）",
        "alipayPublicKey" / "alipay_public_key": "支付宝公钥",
        "signType" / "sign_type": "RSA2",
        "serverUrl" / "server_url": "网关地址（可选）",
        "mode": 1,  // 1=公钥模式, 2=证书模式
        "appCertContent": "商户公钥应用证书(mode=2)",
        "alipayPublicCertContent": "支付宝公钥证书(mode=2)",
        "rootCertContent": "支付宝根证书(mode=2)",
        "notify_url": "异步回调地址（可覆盖默认）",
        "return_url" / "returnUrl": "同步跳转地址",
    }
    """

    def __init__(self, config: dict, notify_url: str):
        self.config = config
        self.notify_url = config.get('notify_url', notify_url)
        self.return_url = config.get('return_url') or config.get('returnUrl', '')

        # 兼容 camelCase 和 snake_case
        app_id = config.get('appId') or config.get('app_id', '')
        raw_private = config.get('privateKey') or config.get('app_private_key', '')
        raw_public = config.get('alipayPublicKey') or config.get('alipay_public_key', '')
        sign_type = config.get('signType') or config.get('sign_type', 'RSA2')
        server_url = config.get('serverUrl') or config.get('server_url', '')
        is_debug = 'sandbox' in server_url if server_url else config.get('debug', False)
        mode = config.get('mode', 1)

        # 自动包装 PEM 头尾
        app_private_key = _wrap_pem(raw_private, 'PRIVATE')
        alipay_public_key = _wrap_pem(raw_public, 'PUBLIC')

        self._gateway = server_url or (
            'https://openapi-sandbox.dl.alipaydev.com/gateway.do' if is_debug
            else 'https://openapi.alipay.com/gateway.do'
        )

        if mode == 2:
            # 证书模式
            from alipay import DCAliPay
            self.client = DCAliPay(
                appid=app_id,
                app_notify_url=self.notify_url,
                app_private_key_string=app_private_key,
                app_public_key_cert_string=config.get('appCertContent') or config.get('app_cert_content', ''),
                alipay_public_key_cert_string=config.get('alipayPublicCertContent') or config.get('alipay_public_cert_content', ''),
                alipay_root_cert_string=config.get('rootCertContent') or config.get('root_cert_content', ''),
                sign_type=sign_type,
                debug=is_debug,
            )
        else:
            # 公钥模式
            from alipay import AliPay
            self.client = AliPay(
                appid=app_id,
                app_notify_url=self.notify_url,
                app_private_key_string=app_private_key,
                alipay_public_key_string=alipay_public_key,
                sign_type=sign_type,
                debug=is_debug,
            )

    def create_page_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        body: str = '',
        return_url: str | None = None,
    ) -> dict[str, Any]:
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            body=body,
            return_url=return_url or self.return_url,
        )
        pay_url = f'{self._gateway}?{order_string}'
        return {'pay_url': pay_url}

    def create_wap_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        body: str = '',
        return_url: str | None = None,
    ) -> dict[str, Any]:
        order_string = self.client.api_alipay_trade_wap_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            body=body,
            return_url=return_url or self.return_url,
        )
        pay_url = f'{self._gateway}?{order_string}'
        return {'pay_url': pay_url}

    def create_qr_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        body: str = '',
    ) -> dict[str, Any]:
        result = self.client.api_alipay_trade_precreate(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            body=body,
        )
        if result.get('code') == '10000':
            return {'qr_code': result.get('qr_code')}
        else:
            log.error(f'支付宝预创建失败: {result}')
            raise Exception(f'支付宝下单失败: {result.get("sub_msg", result.get("msg"))}')

    def query_order(self, order_no: str) -> dict[str, Any]:
        return self.client.api_alipay_trade_query(out_trade_no=order_no)

    def close_order(self, order_no: str) -> bool:
        result = self.client.api_alipay_trade_close(out_trade_no=order_no)
        return result.get('code') == '10000'

    def refund(
        self,
        order_no: str,
        refund_amount_yuan: str,
        refund_reason: str = '',
        out_request_no: str | None = None,
    ) -> dict[str, Any]:
        result = self.client.api_alipay_trade_refund(
            out_trade_no=order_no,
            refund_amount=refund_amount_yuan,
            refund_reason=refund_reason,
            out_request_no=out_request_no,
        )
        if result.get('code') == '10000':
            return result
        else:
            raise Exception(f'支付宝退款失败: {result.get("sub_msg", result.get("msg"))}')

    def verify_callback(self, data: dict) -> bool:
        signature = data.pop('sign', '')
        sign_type = data.pop('sign_type', 'RSA2')
        return self.client.verify(data, signature)

    def create_agreement_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        agreement_sign_params: dict,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            return_url=return_url or self.return_url,
            agreement_sign_params=agreement_sign_params,
        )
        pay_url = f'{self._gateway}?{order_string}'
        return {'pay_url': pay_url, 'sign_type': 'with_payment'}

    def execute_deduction(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        agreement_no: str,
    ) -> dict[str, Any]:
        result = self.client.api_alipay_trade_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            scene='bar_code',
            product_code='CYCLE_PAY_AUTH',
            agreement_params={'agreement_no': agreement_no},
        )
        if result.get('code') == '10000':
            return result
        else:
            raise Exception(f'支付宝代扣失败: {result.get("sub_msg", result.get("msg"))}')


def create_alipay_client(config: dict, notify_url: str) -> AlipayClient:
    """工厂方法"""
    return AlipayClient(config, notify_url)
