from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HasnClients(Base):
    """HASN 节点/客户端设备表（统一节点模型）"""

    __tablename__ = 'hasn_clients'

    id: Mapped[id_key] = mapped_column(init=False)
    client_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='节点唯一标识 (格式: n_{uuid_short} 或旧格式 c_{uuid_short})')
    user_hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='所属 Human 的 hasn_id（格式: h_xxx）')
    client_type: Mapped[str] = mapped_column(sa.String(20), default='', comment='节点类型 (desktop:桌面端:blue/mobile:手机端:green/web:网页端:orange/cloud:云端:purple)')
    device_name: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='设备名称')
    device_info: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='设备信息 (JSONB)')
    api_key_hash: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='节点 API Key 的 SHA256 哈希')
    capacity: Mapped[int] = mapped_column(sa.Integer(), default=1, comment='最大 Agent 承载量（桌面端默认1，云端可配置）')
    last_seen_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后活跃时间')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态 (active:活跃:green/disabled:已禁用:orange/deleted:已删除:red)')
