from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HuanxingUser(Base):
    """唤星用户表"""

    __tablename__ = 'huanxing_user'

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联 sys_user.id')
    server_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='所在服务器ID')
    agent_id: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='Agent ID（如 user-abc123）')
    star_name: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='分身名字')
    template: Mapped[str] = mapped_column(sa.String(64), default='', comment='模板类型：media-creator/side-hustle/finance/office/health/assistant')
    workspace_path: Mapped[str | None] = mapped_column(sa.String(256), default=None, comment='工作区路径')
    agent_status: Mapped[int | None] = mapped_column(sa.SMALLINT(), default=None, comment='Agent状态：1-启用 0-禁用')
    channel_type: Mapped[str | None] = mapped_column(sa.String(16), default=None, comment='注册渠道：feishu/qq/wechat')
    channel_peer_id: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='渠道用户ID')
    remark: Mapped[str | None] = mapped_column(sa.String(512), default=None, comment='备注')
