from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class PayChannel(Base):
    """支付渠道配置表"""

    __tablename__ = 'pay_channel'
    __table_args__ = (
        sa.UniqueConstraint('app_id', 'code', name='uq_pay_channel_app_code'),
        {'comment': '支付渠道配置表'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    app_id: Mapped[int] = mapped_column(sa.BIGINT(), sa.ForeignKey('pay_app.id'), comment='关联支付应用 ID')
    code: Mapped[str] = mapped_column(sa.String(32), comment='渠道编码 wx_native/wx_papay/alipay_pc/alipay_cycle 等')
    name: Mapped[str] = mapped_column(sa.String(64), comment='渠道显示名称')
    status: Mapped[int] = mapped_column(sa.SMALLINT(), default=1, comment='状态 1=启用 0=停用')
    fee_rate: Mapped[Decimal] = mapped_column(sa.NUMERIC(6, 4), default=Decimal('0'), comment='费率（如 0.006 = 0.6%）')
    remark: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment='备注')
    config: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='渠道配置（密钥/证书/appId 等）')
