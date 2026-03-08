from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HxCreatorViralPattern(Base):
    """爆款模式库表"""

    __tablename__ = 'hx_creator_viral_pattern'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='关联项目ID（NULL为全局模式）')
    user_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='关联用户ID（NULL为系统级）')
    platform: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='适用平台')
    category: Mapped[str] = mapped_column(sa.String(30), default='', comment='分类：hook/structure/title/cta/visual/rhythm')
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment='模式名称')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='模式描述')
    template: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='模式模板')
    examples: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='示例JSON数组')
    source: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='来源：manual/ai_extracted/community/system')
    usage_count: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='使用次数')
    success_rate: Mapped[float | None] = mapped_column(sa.REAL(), default=None, comment='成功率')
    tags: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='标签JSON数组')
