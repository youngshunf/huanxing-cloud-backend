from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppResources(Base):
    """App Resource 定义表"""

    __tablename__ = 'app_resources'

    resource_id: Mapped[str] = mapped_column(sa.String(255), primary_key=True, default='', comment='Resource ID')
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    version_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment=None)
    resource_name: Mapped[str] = mapped_column(sa.String(100), default='', comment=None)
    display_name: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    description: Mapped[str] = mapped_column(UniversalText, default='', comment=None)
    schema_json: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment=None)
    storage_strategy: Mapped[str] = mapped_column(sa.String(50), default='', comment='存储策略 (jsonb:JSONB存储:blue/dedicated_table:独立表:green)')
