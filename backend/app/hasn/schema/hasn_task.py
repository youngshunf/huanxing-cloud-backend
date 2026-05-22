from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnTaskSchemaBase(SchemaBase):
    """任务定义基础模型"""
    owner_id: str = Field(description='任务归属 owner')
    agent_id: str = Field(description='执行 agent（必须有绑定 runtime）')
    name: str = Field(description='任务名称')
    description: str | None = Field(None, description='任务描述')
    prompt: str = Field(description='任务指令（支持模板变量）')
    skill_bundle_ids: dict = Field(description='Skill bundle 名称列表，如 ["backend-dev", "mlops"]')
    skill_ids: dict = Field(description='单独 skill 名称列表，如 ["github-pr", "pytest"]')
    workflow_id: int | None = Field(None, description='工作流 ID（可选，未来扩展）')
    enabled_toolsets: dict | None = Field(None, description='限制工具集 ["terminal", "file", "web"]（NULL=全部）')
    context_from_task_id: int | None = Field(None, description='链式任务：注入上次执行结果')
    schedule_type: str = Field(description='调度类型 (once:一次性:blue/interval:间隔:green/cron:定时:orange)')
    schedule_config: dict = Field(description='调度配置 JSON: {expr: "0 9 * * *"} 或 {minutes: 60} 或 {run_at: "2026-05-23T09:00:00Z"}')
    schedule_display: str | None = Field(None, description='人类可读调度描述，如"每天 9:00"')
    enabled: bool = Field(description='是否启用')
    state: str = Field(description='状态 (scheduled:已调度:blue/paused:已暂停:orange/completed:已完成:green/error:异常:red)')
    next_run_at: datetime | None = Field(None, description='下次执行时间')
    last_run_at: datetime | None = Field(None, description='上次执行时间')
    last_status: str | None = Field(None, description='上次执行状态 (ok:成功:green/error:错误:red/silent:静默:gray/timeout:超时:orange)')
    last_error: str | None = Field(None, description='上次错误信息')
    run_count: int = Field(description='总执行次数')
    repeat_times: int | None = Field(None, description='重复次数（NULL=永久，N=执行N次）')
    repeat_completed: int = Field(description='已重复执行次数')
    create_time: datetime = Field(description='创建时间')
    update_time: datetime | None = Field(None, description='更新时间')
    created_by: str | None = Field(None, description='创建者')


class CreateHasnTaskParam(HasnTaskSchemaBase):
    """创建任务定义参数"""


class UpdateHasnTaskParam(HasnTaskSchemaBase):
    """更新任务定义参数"""


class DeleteHasnTaskParam(SchemaBase):
    """删除任务定义参数"""

    pks: list[int] = Field(description='任务定义 ID 列表')


class GetHasnTaskDetail(HasnTaskSchemaBase):
    """任务定义详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
