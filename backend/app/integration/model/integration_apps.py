from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class IntegrationApps(Base):
    """第三方应用集成配置表"""

    __tablename__ = 'integration_apps'

    id: Mapped[id_key] = mapped_column(init=False)
    app_id: Mapped[str] = mapped_column(sa.String(50), default='', comment='应用唯一标识（如 clawhub）')
    app_name: Mapped[str] = mapped_column(sa.String(100), default='', comment='应用名称（如 ClawHub 技能市场）')
    app_type: Mapped[str] = mapped_column(sa.String(50), default='', comment='应用类型（用于实例化对应的集成类，如 clawhub/github/feishu）')
    base_url: Mapped[str] = mapped_column(sa.String(500), default='', comment='应用基础 URL')
    config: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='应用配置（JSON 格式，包含 API 端点、超时设置等）')
    is_enabled: Mapped[bool] = mapped_column(sa.BOOLEAN(), default=True, comment='是否启用')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='应用描述')
    icon_url: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='应用图标 URL')
