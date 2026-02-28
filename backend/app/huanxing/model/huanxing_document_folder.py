from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HuanxingDocumentFolder(Base):
    """唤星文档目录表"""

    __tablename__ = 'huanxing_document_folder'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(sa.String(36), default='', comment='目录UUID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='用户ID')
    name: Mapped[str] = mapped_column(sa.String(255), default='', comment='目录名称')
    parent_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='父目录ID（NULL=根目录）')
    path: Mapped[str] = mapped_column(sa.String(1024), default='/', comment='物化路径，如 /1/5/12/')
    sort_order: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='排序权重（同级内排序）')
    icon: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='目录图标（emoji或icon名）')
    description: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='目录描述')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='更新时间')
    deleted_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='删除时间(软删除)')
