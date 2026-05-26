from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class IntegrationCredentials(Base):
    """用户第三方应用凭证表"""

    __tablename__ = 'integration_credentials'

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='用户 ID')
    app_id: Mapped[str] = mapped_column(sa.String(50), default='', comment='应用唯一标识')
    credentials: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='凭证信息（JSON 格式，如 API Key、Access Token 等）')
    is_active: Mapped[bool] = mapped_column(sa.BOOLEAN(), default=True, comment='是否激活')
    expires_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='凭证过期时间')
