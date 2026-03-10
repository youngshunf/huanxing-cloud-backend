from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HuanxingUserSchemaBase(SchemaBase):
    """唤星用户基础模型"""
    user_id: str = Field(description='平台用户UUID (sys_user.uuid)')
    server_id: str = Field(description='所在服务器ID')
    agent_id: str | None = Field(None, description='Agent ID（如 user-abc123）')
    star_name: str | None = Field(None, description='分身名字')
    template: str = Field(description='模板类型：media-creator/side-hustle/finance/office/health/assistant')
    workspace_path: str | None = Field(None, description='工作区路径')
    agent_status: int | None = Field(None, description='Agent状态：1-启用 0-禁用')
    channel_type: str | None = Field(None, description='注册渠道：feishu/qq/wechat')
    channel_peer_id: str | None = Field(None, description='渠道用户ID')
    remark: str | None = Field(None, description='备注')


class CreateHuanxingUserParam(HuanxingUserSchemaBase):
    """创建唤星用户参数"""


class UpdateHuanxingUserParam(HuanxingUserSchemaBase):
    """更新唤星用户参数"""


class DeleteHuanxingUserParam(SchemaBase):
    """删除唤星用户参数"""

    pks: list[int] = Field(description='唤星用户 ID 列表')


class GetHuanxingUserDetail(HuanxingUserSchemaBase):
    """唤星用户详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None


class AgentSyncUserParam(SchemaBase):
    """Agent 同步用户参数（注册时调用）"""

    user_id: str = Field(description='平台用户 UUID（sys_user.uuid）')
    server_id: str = Field(description='所在服务器 ID')
    agent_id: str = Field(description='Agent ID（如 001-18611348367-assistant）')
    star_name: str | None = Field(None, description='分身名字')
    template: str | None = Field(None, description='模板名称')
    channel_type: str | None = Field(None, description='渠道类型')
    channel_peer_id: str | None = Field(None, description='渠道用户 ID')
    workspace_path: str | None = Field(None, description='工作区路径')


class AgentUpdateUserParam(SchemaBase):
    """Agent 更新用户参数"""

    agent_id: str | None = Field(None, description='Agent ID')
    server_id: str | None = Field(None, description='服务器ID（多 Agent 场景下定位具体记录）')
    star_name: str | None = Field(None, description='分身名字')
    template: str | None = Field(None, description='模板名称')
    workspace_path: str | None = Field(None, description='工作区路径')
    agent_status: int | None = Field(None, description='Agent 状态：1-启用 0-禁用')
