"""
限流器

基于 Redis 实现的限流器，支持滑动窗口算法
"""

from datetime import datetime, timedelta
from typing import Any


class RateLimiter:
    """限流器"""

    def __init__(self, redis_client: Any | None = None):
        """
        初始化限流器

        :param redis_client: Redis 客户端（可选）
        """
        self.redis = redis_client

    async def check(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """
        检查是否超过限流

        :param key: 限流键
        :param max_requests: 最大请求数
        :param window_seconds: 时间窗口（秒）
        :return: True 表示未超限，False 表示超限
        """
        if not self.redis:
            # 如果没有 Redis，暂时不限流
            return True

        # TODO: 实现基于 Redis 的滑动窗口限流
        # 使用 Redis ZSET 实现滑动窗口
        # 1. 移除窗口外的记录
        # 2. 统计窗口内的请求数
        # 3. 如果未超限，添加当前请求
        # 4. 设置过期时间

        return True

    async def get_rate_limit_config(self, scope: str) -> dict[str, int]:
        """
        获取权限的限流配置

        :param scope: 权限标识
        :return: 限流配置
        """
        # 默认限流配置
        default_config = {
            'max_requests': 100,
            'window_seconds': 60,
        }

        # 特定 scope 的限流配置
        scope_configs = {
            'hasn.im.send': {
                'max_requests': 20,
                'window_seconds': 60,
            },
            'hasn.agent.invoke': {
                'max_requests': 10,
                'window_seconds': 60,
            },
        }

        return scope_configs.get(scope, default_config)


# 全局限流器实例（需要在应用启动时初始化 Redis 客户端）
rate_limiter: RateLimiter = RateLimiter()
