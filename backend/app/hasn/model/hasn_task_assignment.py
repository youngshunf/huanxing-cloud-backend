from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, id_key


class HasnTaskAssignment(Base):
    """v2.1 任务执行归属表"""

    __tablename__ = 'hasn_task_assignment'
    __table_args__ = (
        sa.UniqueConstraint(
            'task_uuid',
            name='uq_hasn_task_assignment_task_uuid',
        ),
        {'comment': 'v2.1 任务执行归属表'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    task_uuid: Mapped[str] = mapped_column(sa.String(64), default='', comment='端云稳定任务 UUID')
    owner_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='任务归属 owner')
    agent_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='执行 Agent HASN ID')
    executor_kind: Mapped[str] = mapped_column(sa.String(32), default='local_node', comment='local_node/cloud_runtime_host/unresolved')
    executor_node_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='执行节点 ID')
    binding_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Runtime binding ID')
    assignment_state: Mapped[str] = mapped_column(sa.String(32), default='assigned', comment='assigned/unresolved/stale')
    resolved_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='解析时间')
    stale_after: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='过期时间')
