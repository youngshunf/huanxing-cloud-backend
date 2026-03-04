"""支付模块配置"""

import os

# 支付回调基础 URL — 从环境变量读取，默认本地开发
PAY_ORDER_NOTIFY_URL: str = os.getenv(
    'PAY_ORDER_NOTIFY_URL',
    'https://api.huanxing.ai/api/v1/pay/open/notify',
)

PAY_REFUND_NOTIFY_URL: str = os.getenv(
    'PAY_REFUND_NOTIFY_URL',
    'https://api.huanxing.ai/api/v1/pay/open/refund-notify',
)

PAY_CONTRACT_NOTIFY_URL: str = os.getenv(
    'PAY_CONTRACT_NOTIFY_URL',
    'https://api.huanxing.ai/api/v1/pay/open/contract-notify',
)

# 订单过期时间（分钟）
ORDER_EXPIRE_MINUTES: int = 30

# 套餐价格表（分）— 后续可从数据库读取
TIER_PRICES: dict[str, dict[str, int]] = {
    'star_glow': {'monthly': 4900, 'yearly': 47000},
    'star_shine': {'monthly': 9900, 'yearly': 95000},
    'star_glory': {'monthly': 29900, 'yearly': 287000},
}

# 套餐显示名称
TIER_NAMES: dict[str, str] = {
    'star_glow': '星芒',
    'star_shine': '星辰',
    'star_glory': '星耀',
}
