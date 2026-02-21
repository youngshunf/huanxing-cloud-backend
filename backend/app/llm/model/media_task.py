"""媒体生成任务表"""

from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class MediaTask(Base):
    """媒体生成任务表"""

    __tablename__ = 'llm_media_task'

    id: Mapped[id_key] = mapped_column(init=False)
    task_id: Mapped[str] = mapped_column(sa.String(64), unique=True, index=True, comment='任务 ID (img-xxx / vid-xxx)')
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    api_key_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='API Key ID')
    model_name: Mapped[str] = mapped_column(sa.String(128), index=True, comment='模型名称')
    provider_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='供应商 ID')
    media_type: Mapped[str] = mapped_column(sa.String(16), index=True, comment='媒体类型 (image/video)')
    prompt: Mapped[str] = mapped_column(sa.Text, comment='生成提示词')
    status: Mapped[str] = mapped_column(sa.String(16), default='pending', index=True, comment='任务状态')
    progress: Mapped[int] = mapped_column(default=0, comment='进度 0-100')
    params: Mapped[dict | None] = mapped_column(JSONB, default=None, comment='请求参数 (JSONB)')
    vendor_task_id: Mapped[str | None] = mapped_column(sa.String(128), default=None, index=True, comment='厂商任务 ID')
    vendor_urls: Mapped[list | None] = mapped_column(JSONB, default=None, comment='厂商临时 URL (JSONB)')
    oss_urls: Mapped[list | None] = mapped_column(JSONB, default=None, comment='OSS 永久 URL (JSONB)')
    error_code: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='错误码')
    error_message: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='错误信息')
    webhook_url: Mapped[str | None] = mapped_column(sa.String(512), default=None, comment='Webhook 回调 URL')
    credits_cost: Mapped[Decimal] = mapped_column(sa.Numeric(10, 4), default=Decimal(0), comment='积分消耗')
    credits_pre_deducted: Mapped[Decimal] = mapped_column(sa.Numeric(10, 4), default=Decimal(0), comment='预扣积分')
    poll_count: Mapped[int] = mapped_column(default=0, comment='轮询次数')
    ip_address: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='IP 地址')
    completed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), default=None, comment='完成时间')
