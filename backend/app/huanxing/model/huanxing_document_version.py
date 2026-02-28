from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HuanxingDocumentVersion(Base):
    """文档版本历史表"""

    __tablename__ = 'huanxing_document_version'

    id: Mapped[id_key] = mapped_column(init=False)
    document_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='文档ID')
    version_number: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='版本号')
    title: Mapped[str] = mapped_column(sa.String(255), default='', comment='文档标题')
    content: Mapped[str] = mapped_column(UniversalText, default='', comment='Markdown内容')
    created_by: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='创建者用户ID')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
