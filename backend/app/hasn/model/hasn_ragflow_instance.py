from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class HasnRagflowInstance(Base):
    """RAGFlow 实例配置"""

    __tablename__ = 'hasn_ragflow_instance'

    id: Mapped[id_key] = mapped_column(init=False)
    scope: Mapped[str] = mapped_column(
        sa.String(16), default='public', comment='作用域 (public:公共:blue/enterprise:企业:purple)'
    )
    enterprise_id: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, unique=True, comment='企业 ID')
    url: Mapped[str] = mapped_column(sa.String(512), default='', comment='实例 URL')
    admin_api_key_encrypted: Mapped[bytes] = mapped_column(sa.LargeBinary(), default=b'', comment='管理员 API Key 密文')
    public_pem: Mapped[str] = mapped_column(UniversalText, default='', comment='RSA 公钥')
    default_embd_id: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='默认 Embedding 模型')
    default_llm_id: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='默认 LLM 模型')
    status: Mapped[str] = mapped_column(
        sa.String(16),
        default='pending_config',
        comment='状态 (pending_config:待配置:orange/active:可用:green/disabled:停用:gray)',
    )
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='更新时间')
