from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HasnSkillBundle(Base):
    """Skill Bundle 定义表（多个 skill 的组合）"""

    __tablename__ = 'hasn_skill_bundle'

    id: Mapped[id_key] = mapped_column(init=False)
    owner_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='Bundle 归属 owner')
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment='Bundle 名称（唯一标识）')
    display_name: Mapped[str | None] = mapped_column(sa.String(200), default=None, comment='显示名称')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='描述')
    skill_ids: Mapped[list[str]] = mapped_column(postgresql.JSONB(), default_factory=list, comment='Skill 名称列表，如 ["github-code-review", "test-driven-development"]')
    instruction: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='可选的额外指导语，会在加载 skills 前注入')
    created_time: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_time: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='更新时间')
