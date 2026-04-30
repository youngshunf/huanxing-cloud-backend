from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnTenantSandboxesSchemaBase(SchemaBase):
    """HASN Tenant Sandbox lifecycle 基础模型"""
    sandbox_id: str = Field(description='Sandbox 唯一 ID (sb_{uuid})')
    owner_id: str = Field(description='Owner hasn_id')
    node_id: str | None = Field(None, description='关联 cloud Node ID（可空）')
    image_tier: str = Field(description='镜像层级 (cloud-lite:轻量:green/cloud-cli:CLI增强:blue)')
    state: str = Field(description='状态 (active:运行中:green/sleeping:休眠:blue/deleted:已删除:gray/error:异常:red)')
    router_base_url: str | None = Field(None, description='Tenant Router 公开 base URL；不得保存本地 endpoint/PID')
    resource_profile: dict = Field(description='资源配额摘要 JSON')
    last_health_json: dict = Field(description='最近健康摘要 JSON')
    created_at_remote: datetime | None = Field(None, description='底层 sandbox 创建时间')
    woke_at: datetime | None = Field(None, description='最近唤醒时间')
    slept_at: datetime | None = Field(None, description='最近休眠时间')
    deleted_at: datetime | None = Field(None, description='删除标记时间')
    purge_after: datetime | None = Field(None, description='可物理清理时间（删除后 ETA 24h）')


class CreateHasnTenantSandboxesParam(HasnTenantSandboxesSchemaBase):
    """创建HASN Tenant Sandbox lifecycle 参数"""


class UpdateHasnTenantSandboxesParam(HasnTenantSandboxesSchemaBase):
    """更新HASN Tenant Sandbox lifecycle 参数"""


class DeleteHasnTenantSandboxesParam(SchemaBase):
    """删除HASN Tenant Sandbox lifecycle 参数"""

    pks: list[int] = Field(description='HASN Tenant Sandbox lifecycle  ID 列表')


class GetHasnTenantSandboxesDetail(HasnTenantSandboxesSchemaBase):
    """HASN Tenant Sandbox lifecycle 详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
