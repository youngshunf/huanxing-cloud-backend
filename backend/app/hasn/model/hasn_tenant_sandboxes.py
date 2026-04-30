from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HasnTenantSandboxes(Base):
    """HASN Tenant Sandbox lifecycle 表"""

    __tablename__ = 'hasn_tenant_sandboxes'

    id: Mapped[id_key] = mapped_column(init=False)
    sandbox_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='Sandbox 唯一 ID (sb_{uuid})')
    owner_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='Owner hasn_id')
    node_id: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='关联 cloud Node ID（可空）')
    image_tier: Mapped[str] = mapped_column(sa.String(30), default='', comment='镜像层级 (cloud-lite:轻量:green/cloud-cli:CLI增强:blue)')
    state: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态 (active:运行中:green/sleeping:休眠:blue/deleted:已删除:gray/error:异常:red)')
    router_base_url: Mapped[str | None] = mapped_column(sa.String(300), default=None, comment='Tenant Router 公开 base URL；不得保存本地 endpoint/PID')
    resource_profile: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='资源配额摘要 JSON')
    last_health_json: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='最近健康摘要 JSON')
    created_at_remote: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='底层 sandbox 创建时间')
    woke_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最近唤醒时间')
    slept_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最近休眠时间')
    deleted_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='删除标记时间')
    purge_after: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='可物理清理时间（删除后 ETA 24h）')
