from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HasnTaskRun(Base):
    """任务执行记录表"""

    __tablename__ = 'hasn_task_run'

    id: Mapped[id_key] = mapped_column(init=False)
    task_id: Mapped[int] = mapped_column(sa.BIGINT(), default=0, comment='关联任务 ID')
    agent_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='执行 agent ID')
    runtime_node_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='执行的 hasn-node 节点 ID')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='执行状态 (pending:待执行:blue/running:执行中:orange/success:成功:green/error:失败:red/timeout:超时:orange/silent:静默:gray)')
    started_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='开始执行时间')
    finished_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='完成时间')
    duration_ms: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='执行耗时（毫秒）')
    prompt_snapshot: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='执行时的完整 prompt（包含加载的 skill bundle 和 skill 内容）')
    output: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Agent 最终输出')
    error: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='错误信息')
    model: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='使用的模型')
    token_usage: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='Token 消耗 {input_tokens, output_tokens, total_tokens}')
    create_time: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
