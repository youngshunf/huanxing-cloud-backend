from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HxCreatorDraft(Base):
    """草稿箱表"""

    __tablename__ = 'hx_creator_draft'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    title: Mapped[str | None] = mapped_column(sa.String(200), default=None, comment='标题')
    content: Mapped[str] = mapped_column(UniversalText, default='', comment='内容')
    media: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='媒体文件JSON数组')
    tags: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='标签JSON数组')
    target_platforms: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='目标平台JSON数组')
    meta_data: Mapped[dict | None] = mapped_column('metadata',postgresql.JSONB(), default=None, comment='扩展信息JSON')
