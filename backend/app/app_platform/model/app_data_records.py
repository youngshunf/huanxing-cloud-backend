from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class AppDataRecords(Base):
    """应用数据记录表（JSONB 存储）"""

    __tablename__ = 'app_data_records'

    id: Mapped[id_key] = mapped_column(init=False)
    owner_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='Owner ID')
    app_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='App ID')
    installation_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='Installation ID')
    install_target_type: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='安装目标类型')
    install_target_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='安装目标 ID')
    resource_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='Resource ID')
    record_key: Mapped[str] = mapped_column(sa.String(255), default='', comment='记录键')
    data_json: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='数据 JSON')
    created_by: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='创建者 ID')
    updated_by: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='更新者 ID')
    version: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='版本号')
