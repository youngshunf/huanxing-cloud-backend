import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnHumans(Base):
    """HASN 人类用户身份表"""

    __tablename__ = 'hasn_humans'

    id: Mapped[id_key] = mapped_column(init=False)
    hasn_id: Mapped[str] = mapped_column(sa.String(40), unique=True, comment='HASN 唯一标识 (h_{uuid})')
    star_id: Mapped[str] = mapped_column(sa.String(30), unique=True, comment='唤星号 (数字号或自定义号)')
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), unique=True, comment='关联唤星平台用户 ID')
    name: Mapped[str] = mapped_column(sa.String(50), comment='显示名称')
    bio: Mapped[str | None] = mapped_column(sa.Text(), default=None, comment='个人简介')
    avatar_url: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='头像 URL')
    status: Mapped[str] = mapped_column(sa.String(20), default='active', comment='状态: active/suspended/deleted')
    contact_policy: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='联系人策略')
    timezone: Mapped[str | None] = mapped_column(sa.String(50), default='Asia/Shanghai', comment='时区')
    tags: Mapped[list | None] = mapped_column(postgresql.ARRAY(sa.Text()), default=None, comment='个人标签')
    stats: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='统计信息')
