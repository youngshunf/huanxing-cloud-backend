from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HxCreatorCompetitor(Base):
    """竞品账号表"""

    __tablename__ = 'hx_creator_competitor'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment='竞品名称')
    platform: Mapped[str] = mapped_column(sa.String(50), default='', comment='平台')
    url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='主页链接')
    follower_count: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='粉丝数')
    avg_likes: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='平均点赞')
    content_style: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='内容风格')
    strengths: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='优势')
    notes: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='备注')
    tags: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='标签JSON数组')
    last_analyzed: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后分析时间')
