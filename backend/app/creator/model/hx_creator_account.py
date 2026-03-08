from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HxCreatorAccount(Base):
    """平台账号表"""

    __tablename__ = 'hx_creator_account'

    id: Mapped[id_key] = mapped_column(init=False)
    project_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联项目ID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联用户ID')
    platform: Mapped[str] = mapped_column(sa.String(50), default='', comment='平台标识：xiaohongshu/douyin/wechat/weibo/bilibili')
    platform_uid: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='平台用户ID')
    nickname: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='平台昵称')
    avatar_url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='头像URL')
    bio: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='平台简介')
    home_url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='主页链接')
    followers: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='粉丝数')
    following: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='关注数')
    total_likes: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='总点赞数')
    total_favorites: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='总收藏数')
    total_comments: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='总评论数')
    total_posts: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='总发布数')
    metrics_json: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='更多指标JSON')
    metrics_updated_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='指标更新时间')
    auth_status: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='登录状态：not_configured/active/expired')
    is_primary: Mapped[bool | None] = mapped_column(sa.BOOLEAN(), default=None, comment='是否主账号')
    notes: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='备注')
