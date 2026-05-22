from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HasnTask(Base):
    """任务定义表"""

    __tablename__ = 'hasn_task'

    id: Mapped[id_key] = mapped_column(init=False)
    owner_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='任务归属 owner')
    agent_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='执行 agent（必须有绑定 runtime）')
    name: Mapped[str] = mapped_column(sa.String(200), default='', comment='任务名称')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='任务描述')
    prompt: Mapped[str] = mapped_column(UniversalText, default='', comment='任务指令（支持模板变量）')
    skill_bundle_ids: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='Skill bundle 名称列表，如 ["backend-dev", "mlops"]')
    skill_ids: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='单独 skill 名称列表，如 ["github-pr", "pytest"]')
    workflow_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='工作流 ID（可选，未来扩展）')
    enabled_toolsets: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='限制工具集 ["terminal", "file", "web"]（NULL=全部）')
    context_from_task_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='链式任务：注入上次执行结果')
    schedule_type: Mapped[str] = mapped_column(sa.String(20), default='', comment='调度类型 (once:一次性:blue/interval:间隔:green/cron:定时:orange)')
    schedule_config: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='调度配置 JSON: {expr: "0 9 * * *"} 或 {minutes: 60} 或 {run_at: "2026-05-23T09:00:00Z"}')
    schedule_display: Mapped[str | None] = mapped_column(sa.String(200), default=None, comment='人类可读调度描述，如"每天 9:00"')
    enabled: Mapped[bool] = mapped_column(sa.BOOLEAN(), default=True, comment='是否启用')
    state: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态 (scheduled:已调度:blue/paused:已暂停:orange/completed:已完成:green/error:异常:red)')
    next_run_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='下次执行时间')
    last_run_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='上次执行时间')
    last_status: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='上次执行状态 (ok:成功:green/error:错误:red/silent:静默:gray/timeout:超时:orange)')
    last_error: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='上次错误信息')
    run_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='总执行次数')
    repeat_times: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='重复次数（NULL=永久，N=执行N次）')
    repeat_completed: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='已重复执行次数')
    create_time: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    update_time: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='更新时间')
    created_by: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='创建者')
