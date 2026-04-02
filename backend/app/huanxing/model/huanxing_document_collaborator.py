from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HuanxingDocumentCollaborator(Base):
    """唤星文档协作者/接收者关联表"""

    __tablename__ = 'huanxing_document_collaborator'

    id: Mapped[id_key] = mapped_column(init=False)
    document_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, index=True, comment='原文档ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, index=True, comment='保存该分享的用户ID')
    folder_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='存放在接收者哪个文件夹ID（NULL=根目录）')
    permission: Mapped[str] = mapped_column(sa.String(10), default='view', comment='权限(view只读/edit可编辑)')
    saved_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='保存时间')
