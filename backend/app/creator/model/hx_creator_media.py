from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HxCreatorMedia(Base):
    """素材库表"""

    __tablename__ = 'hx_creator_media'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    type: Mapped[str] = mapped_column(sa.String(20), default='', comment='类型：image/video/audio/template')
    url: Mapped[str] = mapped_column(UniversalText, default='', comment='文件URL')
    filename: Mapped[str] = mapped_column(sa.String(200), default='', comment='文件名')
    size: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='文件大小（字节）')
    width: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='宽度（像素）')
    height: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='高度（像素）')
    duration: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='时长（秒）')
    thumbnail_url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='缩略图URL')
    tags: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='标签JSON数组')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='描述')
