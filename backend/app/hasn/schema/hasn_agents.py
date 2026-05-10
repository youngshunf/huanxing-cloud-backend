from datetime import datetime
from typing import Self
from pydantic import ConfigDict, Field, model_validator

from backend.common.schema import SchemaBase


class HasnAgentsSchemaBase(SchemaBase):
    """HASN Agent 基础模型"""
    hasn_id: str = Field(description='HASN Agent 唯一标识（格式: a_{uuid}）')
    star_id: str = Field(description='Agent 唤星号（如: 100001#star）')
    owner_id: str = Field(description='所属 Human 的 hasn_id')
    name: str | None = Field(None, description='[deprecated] Agent 显示名（迁移期保留，请用 display_name）')
    display_name: str | None = Field(None, description='Agent 显示名（支持中文，对外展示）')
    agent_name: str = Field(description='Agent 标识名')
    description: str | None = Field(None, description='Agent 描述')
    avatar_url: str | None = Field(None, description='[deprecated] 头像 URL（迁移期保留，请用 avatar）')
    avatar: str | None = Field(None, description='头像（与 sys_user.avatar 对齐）')
    type: str = Field(description='Agent 类型 (desktop:桌面端:blue/mobile:手机端:green/cloud:云端:purple/web:网页端:orange)')
    role: str = Field(description='Agent 角色 (primary:主要:blue/specialist:专家:green/service:服务:orange)')
    node_id: str | None = Field(None, description='Agent 驻留节点 ID（设备指纹派生）')
    home_client_id: int | None = Field(None, description='本地 Agent 归属客户端 ID')
    api_key_hash: str = Field(description='API Key 的 SHA256 哈希')
    status: str = Field(description='状态 (active:活跃:green/disabled:已停用:orange/revoked:已吊销:red)')
    created_via: str = Field(description='创建来源 (guardian:Guardian注册:blue/client:客户端创建:green)')

    @model_validator(mode='after')
    def _sync_legacy_fields(self) -> Self:
        # 迁移期双写：display_name↔name、avatar↔avatar_url 任一缺失时互相填充
        if not self.display_name and self.name:
            self.display_name = self.name
        elif not self.name and self.display_name:
            self.name = self.display_name
        if not self.avatar and self.avatar_url:
            self.avatar = self.avatar_url
        elif not self.avatar_url and self.avatar:
            self.avatar_url = self.avatar
        return self


class CreateHasnAgentsParam(HasnAgentsSchemaBase):
    """创建HASN Agent 参数"""


class UpdateHasnAgentsParam(HasnAgentsSchemaBase):
    """更新HASN Agent 参数"""


class DeleteHasnAgentsParam(SchemaBase):
    """删除HASN Agent 参数"""

    pks: list[int] = Field(description='HASN Agent  ID 列表')


class GetHasnAgentsDetail(HasnAgentsSchemaBase):
    """HASN Agent 详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
