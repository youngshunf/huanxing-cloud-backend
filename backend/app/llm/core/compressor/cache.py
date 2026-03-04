"""Redis 缓存层 - 摘要块缓存
@author Guardian

使用消息前缀 hash 匹配缓存，支持增量压缩和多摘要块复用。
多实例部署共享 Redis 缓存。
"""

import hashlib
import json
import random

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from backend.common.log import log

UTC = timezone.utc


@dataclass
class SummaryBlock:
    """单个摘要块"""

    block_id: str
    msg_start_idx: int
    msg_end_idx: int
    summary: str
    token_count: int
    created_at: str  # ISO 格式字符串，便于 JSON 序列化

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'SummaryBlock':
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ConversationCache:
    """对话级压缩缓存"""

    prefix_hash: str
    total_compressed_msg: int
    summary_blocks: list[SummaryBlock] = field(default_factory=list)
    created_at: str = ''
    updated_at: str = ''

    def to_json(self) -> str:
        data = {
            'prefix_hash': self.prefix_hash,
            'total_compressed_msg': self.total_compressed_msg,
            'summary_blocks': [b.to_dict() for b in self.summary_blocks],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> 'ConversationCache':
        data = json.loads(raw)
        blocks = [SummaryBlock.from_dict(b) for b in data.get('summary_blocks', [])]
        return cls(
            prefix_hash=data['prefix_hash'],
            total_compressed_msg=data['total_compressed_msg'],
            summary_blocks=blocks,
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
        )


class CompressCache:
    """Redis 压缩缓存"""

    def __init__(self, config) -> None:
        self.prefix = config.cache_prefix
        self.ttl = config.cache_ttl
        self.enabled = config.cache_enabled
        self._redis = None

    @property
    def redis(self):
        if self._redis is None:
            from backend.database.redis import redis_client
            self._redis = redis_client
        return self._redis

    @staticmethod
    def compute_prefix_hash(messages: list[dict], count: int) -> str:
        """计算消息前缀的 SHA256 hash"""
        parts = []
        for msg in messages[:count]:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if isinstance(content, list):
                content = json.dumps(content, sort_keys=True, ensure_ascii=False)
            elif not isinstance(content, str):
                content = str(content)
            parts.append(f'{role}:{content}')

        raw = '|'.join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()

    async def find_matching(self, messages: list[dict]) -> tuple[list[SummaryBlock] | None, int]:
        """
        查找匹配的缓存。从消息数最多的开始匹配（贪心策略）。

        Returns:
            (摘要块列表, 匹配的消息数)，未命中返回 (None, 0)
        """
        if not self.enabled:
            return None, 0

        try:
            msg_len = len(messages)

            # 获取所有消息数量索引
            idx_keys = await self.redis.keys(f'{self.prefix}:idx:*')
            if not idx_keys:
                return None, 0

            # 降序排列，优先匹配更多消息的缓存
            msg_counts = sorted(
                [int(k.rsplit(':', 1)[-1]) for k in idx_keys],
                reverse=True,
            )

            for count in msg_counts:
                if count > msg_len:
                    continue

                prefix_hash = self.compute_prefix_hash(messages, count)
                exists = await self.redis.sismember(f'{self.prefix}:idx:{count}', prefix_hash)
                if not exists:
                    continue

                cache_data = await self.redis.get(f'{self.prefix}:prefix:{prefix_hash}')
                if not cache_data:
                    continue

                cache = ConversationCache.from_json(cache_data)
                log.info(
                    f'[智能压缩] Redis 缓存命中 - 复用 {count} 条消息的 '
                    f'{len(cache.summary_blocks)} 个摘要块'
                )
                return cache.summary_blocks, cache.total_compressed_msg

            return None, 0

        except Exception as e:
            log.warning(f'[智能压缩] Redis 缓存查找失败，跳过缓存: {e}')
            return None, 0

    async def save(self, messages: list[dict], compressed_count: int, blocks: list[SummaryBlock]) -> None:
        """保存缓存到 Redis"""
        if not self.enabled:
            return

        try:
            prefix_hash = self.compute_prefix_hash(messages, compressed_count)
            now = datetime.now(UTC).isoformat()

            cache = ConversationCache(
                prefix_hash=prefix_hash,
                total_compressed_msg=compressed_count,
                summary_blocks=blocks,
                created_at=now,
                updated_at=now,
            )

            # TTL 加随机抖动（±10%），防止缓存雪崩
            jitter = random.randint(-self.ttl // 10, self.ttl // 10)
            ttl = self.ttl + jitter

            pipe = self.redis.pipeline()
            pipe.set(f'{self.prefix}:prefix:{prefix_hash}', cache.to_json(), ex=ttl)
            pipe.sadd(f'{self.prefix}:idx:{compressed_count}', prefix_hash)
            pipe.expire(f'{self.prefix}:idx:{compressed_count}', ttl)
            await pipe.execute()

            log.debug(
                f'[智能压缩] 缓存已保存 - {compressed_count} 条消息, '
                f'{len(blocks)} 个摘要块, TTL={ttl}s'
            )

        except Exception as e:
            log.warning(f'[智能压缩] Redis 缓存保存失败，忽略: {e}')
