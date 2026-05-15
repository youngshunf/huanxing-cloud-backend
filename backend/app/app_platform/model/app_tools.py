from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppTools(Base):
    """App Tool 定义表"""

    __tablename__ = 'app_tools'

    tool_id: Mapped[str] = mapped_column(sa.String(255), primary_key=True, default='', comment='Tool ID')
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    version_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment=None)
    tool_name: Mapped[str] = mapped_column(sa.String(100), default='', comment=None)
    display_name: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    description: Mapped[str] = mapped_column(UniversalText, default='', comment=None)
    input_schema: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment=None)
    output_schema: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment=None)
    visibility: Mapped[str] = mapped_column(sa.String(50), default='', comment='可见性 (private:私有:gray/public_service:公开服务:green)')
    risk_level: Mapped[str] = mapped_column(sa.String(50), default='', comment='风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)')
    required_scopes: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment=None)
