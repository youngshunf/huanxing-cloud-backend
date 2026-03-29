from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HasnTradeSessions(Base):
    """HASN 交易会话表"""

    __tablename__ = 'hasn_trade_sessions'

    id: Mapped[id_key] = mapped_column(init=False)
    buyer_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='买方 hasn_id')
    seller_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='卖方 hasn_id')
    relation_type: Mapped[str] = mapped_column(sa.String(20), default='', comment='关系类型 (commerce:商业:orange/service:履约:green)')
    scope: Mapped[str] = mapped_column(sa.String(30), default='', comment='当前作用域 (pre_sale:售前咨询:blue/in_order:订单进行中:orange/after_sale:售后:green/active_order:配送中:cyan/subscription:已订阅:purple)')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态 (active:进行中:green/completed:已完成:blue/archived:已归档:gray/cancelled:已取消:red)')
    order_id: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='关联订单 ID')
    expires_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='过期时间')
    meta_data: Mapped[dict] = mapped_column('metadata',postgresql.JSONB(), default_factory=dict, comment='附加元数据 (JSONB)')
