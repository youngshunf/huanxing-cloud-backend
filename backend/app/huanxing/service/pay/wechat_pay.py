"""微信支付 V3 SDK 封装 — 从数据库读取配置"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from wechatpayv3 import WeChatPay, WeChatPayType

from backend.common.log import log

logger = logging.getLogger(__name__)


class WechatPayClient:
    """微信支付客户端（从 PayChannel.config JSONB 读取配置）
    
    config JSONB 字段说明:
    {
        "mch_id": "商户号",
        "appid": "公众号/小程序AppID（JSAPI/小程序用）",
        "apiv3_key": "APIv3 密钥（32字节）",
        "cert_serial_no": "商户API证书序列号",
        "private_key": "商户API私钥（PEM格式文本，含BEGIN/END）",
        "notify_url": "支付回调地址（可覆盖默认）"
    }
    """

    def __init__(self, config: dict, notify_url: str):
        self.config = config
        self.notify_url = config.get('notify_url', notify_url)
        
        private_key = config['private_key']
        # 支持直接 PEM 文本或文件路径
        if private_key.startswith('-----BEGIN'):
            private_key_string = private_key
        else:
            with open(private_key, 'r') as f:
                private_key_string = f.read()

        self.client = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=config['mch_id'],
            private_key=private_key_string,
            cert_serial_no=config['cert_serial_no'],
            apiv3_key=config['apiv3_key'],
            appid=config.get('appid', ''),
            notify_url=self.notify_url,
        )

    def create_native_order(
        self,
        order_no: str,
        amount: int,
        description: str,
        expire_minutes: int = 30,
    ) -> dict[str, Any]:
        """创建 Native 扫码支付订单
        
        :param order_no: 商户订单号
        :param amount: 金额（分）
        :param description: 订单描述
        :param expire_minutes: 过期时间（分钟）
        :return: {"code_url": "weixin://...", "prepay_id": "..."}
        """
        expire_time = (datetime.now() + timedelta(minutes=expire_minutes)).strftime('%Y-%m-%dT%H:%M:%S+08:00')
        
        code, response = self.client.pay(
            description=description,
            out_trade_no=order_no,
            amount={'total': amount, 'currency': 'CNY'},
            time_expire=expire_time,
        )

        if code == 200:
            data = json.loads(response) if isinstance(response, str) else response
            return {'code_url': data.get('code_url'), 'prepay_id': data.get('prepay_id')}
        else:
            log.error(f'微信下单失败: code={code}, response={response}')
            raise Exception(f'微信支付下单失败: {response}')

    def create_h5_order(
        self,
        order_no: str,
        amount: int,
        description: str,
        payer_client_ip: str,
        expire_minutes: int = 30,
    ) -> dict[str, Any]:
        """创建 H5 支付订单"""
        expire_time = (datetime.now() + timedelta(minutes=expire_minutes)).strftime('%Y-%m-%dT%H:%M:%S+08:00')
        
        code, response = self.client.pay(
            description=description,
            out_trade_no=order_no,
            amount={'total': amount, 'currency': 'CNY'},
            time_expire=expire_time,
            scene_info={
                'payer_client_ip': payer_client_ip,
                'h5_info': {'type': 'Wap'},
            },
            pay_type=WeChatPayType.H5,
        )

        if code == 200:
            data = json.loads(response) if isinstance(response, str) else response
            return {'h5_url': data.get('h5_url')}
        else:
            log.error(f'微信H5下单失败: code={code}, response={response}')
            raise Exception(f'微信H5支付下单失败: {response}')

    def query_order(self, order_no: str) -> dict[str, Any]:
        """查询订单状态"""
        code, response = self.client.query(out_trade_no=order_no)
        if code == 200:
            return json.loads(response) if isinstance(response, str) else response
        else:
            raise Exception(f'微信查单失败: {response}')

    def close_order(self, order_no: str) -> bool:
        """关闭订单"""
        code, response = self.client.close(out_trade_no=order_no)
        return code in (200, 204)

    def refund(
        self,
        order_no: str,
        refund_no: str,
        refund_amount: int,
        total_amount: int,
        reason: str = '',
        notify_url: str | None = None,
    ) -> dict[str, Any]:
        """申请退款"""
        code, response = self.client.refund(
            out_trade_no=order_no,
            out_refund_no=refund_no,
            amount={
                'refund': refund_amount,
                'total': total_amount,
                'currency': 'CNY',
            },
            reason=reason,
            notify_url=notify_url,
        )
        if code == 200:
            return json.loads(response) if isinstance(response, str) else response
        else:
            raise Exception(f'微信退款失败: {response}')

    def verify_and_decrypt_callback(self, headers: dict, body: str) -> dict[str, Any]:
        """验证回调签名并解密数据
        
        :param headers: 请求头（需要 Wechatpay-Timestamp, Wechatpay-Nonce, Wechatpay-Signature, Wechatpay-Serial）
        :param body: 请求体原始字符串
        :return: 解密后的通知数据
        """
        result = self.client.callback(headers=headers, body=body)
        if result:
            return json.loads(result) if isinstance(result, str) else result
        raise Exception('微信回调验签失败')

    # ============================================================
    # 委托代扣（自动续费签约）
    # ============================================================

    def create_sign_order(
        self,
        order_no: str,
        amount: int,
        description: str,
        contract_no: str,
        plan_id: str,
        contract_display_account: str = '',
        expire_minutes: int = 30,
    ) -> dict[str, Any]:
        """
        创建 Native 支付中签约订单（papay V2 "支付中签约"）
        
        NOTE: 微信 papay V2 的"支付中签约"接口需要额外开通权限。
        如果未开通，可以分两步：1) 先正常支付 2) 再引导签约。
        
        此方法使用 sign() 方法，具体参数需根据微信文档调整。
        """
        # 先创建普通支付订单
        result = self.create_native_order(order_no, amount, description, expire_minutes)
        
        # TODO: 如果开通了 papay V2 权限，使用 self.client.sign() 创建签约
        # 暂时返回支付结果 + contract_no，前端在支付成功后再引导签约
        result['contract_no'] = contract_no
        result['sign_type'] = 'post_payment'  # 标记为 "支付后签约"
        
        return result


def create_wechat_client(config: dict, notify_url: str) -> WechatPayClient:
    """工厂方法"""
    return WechatPayClient(config, notify_url)
