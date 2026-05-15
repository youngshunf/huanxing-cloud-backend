from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppAgentBindingsSchemaBase(SchemaBase):
    """Installation 绑定的 Agent 列基础模型"""
    binding_id: str | UUID = Field(description='绑定 ID')
    installation_id: str = Field(description='None')
    agent_id: str = Field(description='None')
    bound_at: datetime = Field(description='None')
    bound_by: str = Field(description='None')
    status: str = Field(description='状态 (active:生效:green/revoked:已撤销:red)')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppAgentBindingsParam(AppAgentBindingsSchemaBase):
    """创建Installation 绑定的 Agent 列参数"""


class UpdateAppAgentBindingsParam(AppAgentBindingsSchemaBase):
    """更新Installation 绑定的 Agent 列参数"""


class DeleteAppAgentBindingsParam(SchemaBase):
    """删除Installation 绑定的 Agent 列参数"""

    pks: list[int] = Field(description='Installation 绑定的 Agent 列 ID 列表')


class GetAppAgentBindingsDetail(AppAgentBindingsSchemaBase):
    """Installation 绑定的 Agent 列详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
