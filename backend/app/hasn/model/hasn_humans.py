from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


class HasnHumans(Base):
    """HASN 人类用户身份表"""

    __tablename__ = 'hasn_humans'

    id: Mapped[id_key] = mapped_column(init=False)
    hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='HASN 唯一标识 (h_{uuid})')
    star_id: Mapped[str] = mapped_column(sa.String(30), default='', comment='唤星号 (数字号或自定义号)')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联唤星平台用户 ID')
    name: Mapped[str] = mapped_column(sa.String(50), default='', comment='[deprecated] 显示名称（迁移期保留，新代码请用 nickname）')
    nickname: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='昵称（与 sys_user.nickname 对齐）')
    bio: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='个人简介')
    avatar_url: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='[deprecated] 头像 URL（迁移期保留，新代码请用 avatar）')
    avatar: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='头像（与 sys_user.avatar 对齐）')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态 (active:正常:green/suspended:已暂停:orange/deleted:已注销:red)')
    contact_policy: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='联系人策略 (JSONB)')
    timezone: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='时区')
    tags: Mapped[list | None] = mapped_column(postgresql.ARRAY(sa.Text()), default=None, comment='个人标签')
    stats: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='统计信息 (JSONB)')
