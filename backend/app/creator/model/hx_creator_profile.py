from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HxCreatorProfile(Base):
    """账号画像表"""

    __tablename__ = 'hx_creator_profile'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    niche: Mapped[str] = mapped_column(sa.String(100), default='', comment='赛道/领域：美食、旅行、科技、教育')
    sub_niche: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='细分赛道：家常菜、烘焙、减脂餐')
    persona: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='人设：美食达人/料理小白/专业厨师')
    target_audience: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='目标受众描述')
    tone: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='内容调性：轻松幽默/专业严谨/温暖治愈')
    keywords: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='核心关键词JSON数组')
    bio: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='简介文案')
    content_pillars: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='内容支柱JSON数组')
    posting_frequency: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='发布频率：如每周3-4篇')
    best_posting_time: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='最佳发布时间')
    style_references: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='风格参考账号JSON数组')
    taboo_topics: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='避免话题JSON数组')
    pillar_weights: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='支柱权重JSON（根据数据反馈调整）')
    pillar_weights_updated_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='支柱权重更新时间')
