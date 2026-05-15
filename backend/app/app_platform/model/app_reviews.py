from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppReviews(Base):
    """App 审核记录表"""

    __tablename__ = 'app_reviews'

    review_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='审核 ID')
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    version_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment=None)
    review_type: Mapped[str] = mapped_column(sa.String(50), default='', comment='审核类型 (content:内容审核:blue/security:安全审核:red/ui:UI审核:green/frontend:前端审核:purple)')
    reviewer_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    review_status: Mapped[str] = mapped_column(sa.String(50), default='', comment='审核状态 (pending:待审核:blue/approved:已批准:green/rejected:已拒绝:red/changes_requested:需要修改:orange)')
    review_notes: Mapped[str | None] = mapped_column(UniversalText, default=None, comment=None)
