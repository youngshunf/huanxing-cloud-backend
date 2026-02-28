"""支付宝 SDK 封装 — 从数据库读取配置"""

import json
import logging
from typing import Any

from alipay import AliPay

from backend.common.log import log

logger = logging.getLogger(__name__)


class AlipayClient:
    """支付宝支付客户端（从 PayChannel.config JSONB 读取配置）
    
    config JSONB 字段说明:
    {
        "app_id": "支付宝应用ID",
        "app_private_key": "应用私钥（PEM格式文本，不含BEGIN/END也可）",
        "alipay_public_key": "支付宝公钥（PEM格式文本）",
        "sign_type": "RSA2",
        "notify_url": "异步回调地址（可覆盖默认）",
        "return_url": "同步跳转地址",
        "debug": false
    }
    """

    def __init__(self, config: dict, notify_url: str):
        self.config = config
        self.notify_url = config.get('notify_url', notify_url)
        self.return_url = config.get('return_url', '')

        app_private_key = config['app_private_key']
        alipay_public_key = config['alipay_public_key']

        # python-alipay-sdk 接受字符串格式的密钥
        self.client = AliPay(
            appid=config['app_id'],
            app_notify_url=self.notify_url,
            app_private_key_string=app_private_key,
            alipay_public_key_string=alipay_public_key,
            sign_type=config.get('sign_type', 'RSA2'),
            debug=config.get('debug', False),
        )

    def create_page_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        body: str = '',
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """创建电脑网站支付（alipay.trade.page.pay）
        
        :param order_no: 商户订单号
        :param amount_yuan: 金额（元，字符串，如 "49.00"）
        :param subject: 订单标题
        :param body: 订单描述
        :param return_url: 支付后跳转地址
        :return: {"pay_url": "https://..."}
        """
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            body=body,
            return_url=return_url or self.return_url,
        )
        # order_string 是查询字符串，拼上支付宝网关
        gateway = 'https://openapi.alipay.com/gateway.do'
        if self.config.get('debug'):
            gateway = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'

        pay_url = f'{gateway}?{order_string}'
        return {'pay_url': pay_url}

    def create_wap_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        body: str = '',
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """创建手机网站支付（alipay.trade.wap.pay）"""
        order_string = self.client.api_alipay_trade_wap_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            body=body,
            return_url=return_url or self.return_url,
        )
        gateway = 'https://openapi.alipay.com/gateway.do'
        if self.config.get('debug'):
            gateway = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'

        pay_url = f'{gateway}?{order_string}'
        return {'pay_url': pay_url}

    def create_qr_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        body: str = '',
    ) -> dict[str, Any]:
        """创建当面付（扫码支付，alipay.trade.precreate）"""
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
        """查询订单"""
        result = self.client.api_alipay_trade_query(out_trade_no=order_no)
        return result

    def close_order(self, order_no: str) -> bool:
        """关闭订单"""
        result = self.client.api_alipay_trade_close(out_trade_no=order_no)
        return result.get('code') == '10000'

    def refund(
        self,
        order_no: str,
        refund_amount_yuan: str,
        refund_reason: str = '',
        out_request_no: str | None = None,
    ) -> dict[str, Any]:
        """退款"""
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
        """验证异步回调签名
        
        :param data: 回调 form 数据（dict）
        :return: 是否验签通过
        """
        # python-alipay-sdk 的 verify 方法
        signature = data.pop('sign', '')
        sign_type = data.pop('sign_type', 'RSA2')
        return self.client.verify(data, signature)

    # ============================================================
    # 周期扣款（自动续费）
    # ============================================================

    def create_agreement_pay(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        agreement_sign_params: dict,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """
        创建 "支付并签约" 订单（周期扣款 CYCLE_PAY_AUTH）
        
        agreement_sign_params 示例:
        {
            "personal_product_code": "CYCLE_PAY_AUTH_P",
            "sign_scene": "INDUSTRY|DIGITAL_MEDIA",
            "period_rule_params": {
                "period_type": "MONTH",
                "period": 1,
                "execute_time": "2026-04-01",
                "single_amount": "49.00",
                "total_amount": "588.00",
                "total_payments": 12
            },
            "access_params": {
                "channel": "ALIPAYAPP"
            }
        }
        
        NOTE: 需在支付宝开放平台开通 CYCLE_PAY_AUTH 能力。
        此方法通过 server_api 调用 alipay.trade.page.pay + 签约扩展参数。
        """
        # 使用 api_alipay_trade_page_pay 并传入 agreement_sign_params
        # python-alipay-sdk 的 page_pay 支持 kwargs
        order_string = self.client.api_alipay_trade_page_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            return_url=return_url or self.return_url,
            agreement_sign_params=agreement_sign_params,
        )
        gateway = 'https://openapi.alipay.com/gateway.do'
        if self.config.get('debug'):
            gateway = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'

        pay_url = f'{gateway}?{order_string}'
        return {'pay_url': pay_url, 'sign_type': 'with_payment'}

    def execute_deduction(
        self,
        order_no: str,
        amount_yuan: str,
        subject: str,
        agreement_no: str,
    ) -> dict[str, Any]:
        """
        执行代扣（alipay.trade.pay 约定扣款）
        
        :param agreement_no: 支付宝签约协议号
        """
        result = self.client.api_alipay_trade_pay(
            out_trade_no=order_no,
            total_amount=amount_yuan,
            subject=subject,
            scene='bar_code',  # 周期扣款场景
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
