from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HxCreatorPublish(Base):
    """发布记录表"""

    __tablename__ = 'hx_creator_publish'

    id: Mapped[id_key] = mapped_column(init=False)
    content_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联内容ID')
    account_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='关联平台账号ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    platform: Mapped[str] = mapped_column(sa.String(50), default='', comment='发布平台')
    publish_url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='发布链接')
    status: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='状态：pending/published/failed/deleted')
    method: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='发布方式：manual/auto/scheduled')
    error_message: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='错误信息')
    published_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='发布时间')
    views: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='阅读量')
    likes: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='点赞数')
    comments: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='评论数')
    shares: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='分享数')
    favorites: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='收藏数')
    metrics_json: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='更多数据指标JSON')
    metrics_updated_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='指标更新时间')
