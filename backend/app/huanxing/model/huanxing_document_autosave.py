from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HuanxingDocumentAutosave(Base):
    """文档自动保存表（每文档每用户仅一条，UPSERT更新）"""

    __tablename__ = 'huanxing_document_autosave'

    id: Mapped[id_key] = mapped_column(init=False)
    document_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='文档ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='用户ID')
    content: Mapped[str] = mapped_column(UniversalText, default='', comment='Markdown内容')
    saved_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='最后保存时间')
