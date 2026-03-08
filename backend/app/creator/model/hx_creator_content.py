from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HxCreatorContent(Base):
    """内容创作主表"""

    __tablename__ = 'hx_creator_content'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    title: Mapped[str | None] = mapped_column(sa.String(200), default=None, comment='内容标题')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态：idea/researching/drafting/reviewing/ready/published/analyzing/completed/archived')
    target_platforms: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='目标平台JSON数组')
    pipeline_mode: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='流水线模式：manual/semi-auto/auto')
    content_tracks: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='创作轨道：article/video/article,video')
    viral_pattern_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='使用的爆款模式ID')
    meta_data: Mapped[dict | None] = mapped_column('metadata',postgresql.JSONB(), default=None, comment='扩展信息JSON')
