from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HxCreatorProject(Base):
    """创作项目表"""

    __tablename__ = 'hx_creator_project'

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment='项目名称（如：小红书美食号）')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='项目描述')
    platform: Mapped[str] = mapped_column(sa.String(50), default='', comment='主平台：xiaohongshu/douyin/wechat/weibo/bilibili')
    platforms: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='多平台JSON数组')
    avatar_url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='项目头像URL')
    is_active: Mapped[bool | None] = mapped_column(sa.BOOLEAN(), default=None, comment='是否为当前活跃项目')
