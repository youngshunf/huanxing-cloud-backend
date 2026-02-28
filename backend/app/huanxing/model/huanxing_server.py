from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HuanxingServer(Base):
    """唤星服务器表"""

    __tablename__ = 'huanxing_server'

    id: Mapped[id_key] = mapped_column(init=False)
    server_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='服务器唯一标识（如 server-001）')
    server_name: Mapped[str | None] = mapped_column(sa.String(128), default=None, comment='服务器名称（如 京东云-华北1）')
    ip_address: Mapped[str] = mapped_column(sa.String(45), default='', comment='服务器IP地址')
    port: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='SSH端口')
    region: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='地域（如 cn-north-1）')
    provider: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='云服务商（如 jdcloud/aliyun/tencent）')
    max_users: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='最大用户容量')
    status: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='状态(published已发布/disabled禁用/draft草稿/archived已归档)')
    gateway_status: Mapped[str | None] = mapped_column(sa.String(16), default=None, comment='Gateway状态: running/stopped/unknown')
    last_heartbeat: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后心跳时间')
    config: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='服务器配置信息（JSON）')
    remark: Mapped[str | None] = mapped_column(sa.String(512), default=None, comment='备注')
