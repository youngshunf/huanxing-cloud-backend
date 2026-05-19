from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class HasnRagflowCredential(Base):
    """RAGFlow 用户凭据映射"""

    __tablename__ = 'hasn_ragflow_credential'

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='用户 ID')
    instance_id: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='实例 ID')
    ragflow_user_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='RAGFlow 用户 ID')
    ragflow_tenant_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='RAGFlow Tenant ID')
    api_key_encrypted: Mapped[bytes] = mapped_column(sa.LargeBinary(), default=b'', comment='API Key 密文')
    status: Mapped[str] = mapped_column(
        sa.String(16),
        default='pending',
        comment='状态 (pending:待provision:gray/active:已激活:green/failed:失败:red/revoked:已撤销:default)',
    )
    last_error: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='最后错误')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='更新时间')
