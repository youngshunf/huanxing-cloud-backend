"""压缩用量日志表 - 追踪平台承担的摘要生成成本"""

from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class CompressUsageLog(Base):
    """压缩用量日志表"""

    __tablename__ = 'llm_compress_usage_log'

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    api_key_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='API Key ID')
    request_id: Mapped[str] = mapped_column(sa.String(64), index=True, comment='关联的用户请求 ID')
    summary_model: Mapped[str] = mapped_column(sa.String(128), comment='摘要生成模型')
    input_tokens: Mapped[int] = mapped_column(default=0, comment='摘要输入 tokens')
    output_tokens: Mapped[int] = mapped_column(default=0, comment='摘要输出 tokens')
    input_cost: Mapped[Decimal] = mapped_column(sa.Numeric(10, 6), default=Decimal(0), comment='输入成本 (USD)')
    output_cost: Mapped[Decimal] = mapped_column(sa.Numeric(10, 6), default=Decimal(0), comment='输出成本 (USD)')
    total_cost: Mapped[Decimal] = mapped_column(sa.Numeric(10, 6), default=Decimal(0), comment='总成本 (USD)')
    original_messages: Mapped[int] = mapped_column(default=0, comment='原始消息数')
    compressed_messages: Mapped[int] = mapped_column(default=0, comment='压缩后消息数')
    original_tokens: Mapped[int] = mapped_column(default=0, comment='压缩前估算 token')
    compressed_tokens: Mapped[int] = mapped_column(default=0, comment='压缩后估算 token')
    summary_blocks: Mapped[int] = mapped_column(default=0, comment='摘要块数')
    cache_hit: Mapped[bool] = mapped_column(default=False, comment='是否缓存命中')
    secondary_compression: Mapped[bool] = mapped_column(default=False, comment='是否二次压缩')
    degraded_keep_count: Mapped[int | None] = mapped_column(default=None, comment='降级保留消息数')
    generation_ms: Mapped[int] = mapped_column(default=0, comment='摘要生成耗时(ms)')
    ip_address: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='IP 地址')
