from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HxCreatorTopic(Base):
    """选题推荐表"""

    __tablename__ = 'hx_creator_topic'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    title: Mapped[str] = mapped_column(sa.String(200), default='', comment='选题标题')
    potential_score: Mapped[float | None] = mapped_column(sa.REAL(), default=None, comment='潜力评分')
    heat_index: Mapped[float | None] = mapped_column(sa.REAL(), default=None, comment='热度指数')
    reason: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='推荐理由')
    keywords: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='关键词JSON数组')
    creative_angles: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='创作角度JSON')
    status: Mapped[int] = mapped_column(sa.SMALLINT(), default=0, comment='状态：0-待处理 1-已采纳 2-已跳过')
    content_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='采纳后关联的内容ID')
    batch_date: Mapped[str | None] = mapped_column(sa.String(10), default=None, comment='批次日期')
    source_uid: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='来源标识')
