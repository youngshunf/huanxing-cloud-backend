"""HASN Agent管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnAgentSchemaBase(SchemaBase):
    """Agent基础 Schema"""
    star_id: str = Field(description='唤星号')
    owner_id: str = Field(description='所属用户hasn_id')
    name: str = Field(description='Agent名称')
    api_key_prefix: str | None = Field(None, description='API Key前缀')
    openclaw_agent_id: str | None = Field(None, description='OpenClaw Agent ID')
    description: str | None = Field(None, description='描述')
    role: str | None = Field(None, description='角色')
    capabilities: list | None = Field(None, description='能力列表(JSON array)')
    profile: dict | None = Field(None, description='扩展资料(JSON)')
    api_endpoint: str | None = Field(None, description='API端点')
    pricing: dict | None = Field(None, description='定价策略(JSON)')
    reputation_score: float | None = Field(None, description='信誉分')
    status: str | None = Field(None, description='状态')
    last_active_at: datetime | None = Field(None, description='最后活跃时间')


class CreateHasnAgentParam(HasnAgentSchemaBase):
    """创建Agent参数"""


class UpdateHasnAgentParam(HasnAgentSchemaBase):
    """更新Agent参数"""


class DeleteHasnAgentParam(SchemaBase):
    """删除Agent参数"""
    pks: list[str] = Field(description='Agent ID 列表')


class GetHasnAgentDetail(HasnAgentSchemaBase):
    """Agent详情"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_time: datetime
    updated_time: datetime | None = None
