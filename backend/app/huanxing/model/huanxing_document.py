from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HuanxingDocument(Base):
    """唤星文档表"""

    __tablename__ = 'huanxing_document'

    id: Mapped[id_key] = mapped_column(init=False)
    uuid: Mapped[str] = mapped_column(sa.String(36), default='', comment='文档UUID')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='用户ID')
    folder_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='目录ID（NULL=根目录）')
    title: Mapped[str] = mapped_column(sa.String(255), default='', comment='文档标题')
    content: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Markdown内容')
    summary: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='摘要（自动截取或手动设置）')
    tags: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='标签（JSON数组）')
    word_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='字数统计')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态(draft草稿/published已发布/archived已归档)')
    is_public: Mapped[bool] = mapped_column(sa.BOOLEAN(), default=True, comment='是否公开')
    created_by: Mapped[str] = mapped_column(sa.String(20), default='', comment='创建来源(user用户/agent智能体)')
    agent_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Agent ID')
    share_token: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='分享链接token')
    share_password: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='分享密码(bcrypt hash)')
    share_permission: Mapped[str | None] = mapped_column(sa.String(10), default=None, comment='分享权限(view只读/edit可编辑)')
    share_expires_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='分享链接过期时间')
    current_version: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='当前版本号')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='更新时间')
    deleted_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='删除时间(软删除)')
