from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HuanxingServerSchemaBase(SchemaBase):
    """唤星服务器基础模型"""
    server_id: str = Field(description='服务器唯一标识（如 server-001）')
    server_name: str | None = Field(None, description='服务器名称（如 京东云-华北1）')
    ip_address: str = Field(description='服务器IP地址')
    port: int | None = Field(None, description='SSH端口')
    region: str | None = Field(None, description='地域（如 cn-north-1）')
    provider: str | None = Field(None, description='云服务商（如 jdcloud/aliyun/tencent）')
    max_users: int | None = Field(None, description='最大用户容量')
    status: str | None = Field(None, description='状态(published/disabled/draft/archived)')
    gateway_status: str | None = Field(None, description='Gateway状态: running/stopped/unknown')
    last_heartbeat: datetime | None = Field(None, description='最后心跳时间')
    config: dict | None = Field(None, description='服务器配置信息（JSON）')
    remark: str | None = Field(None, description='备注')


class CreateHuanxingServerParam(HuanxingServerSchemaBase):
    """创建唤星服务器参数"""


class UpdateHuanxingServerParam(HuanxingServerSchemaBase):
    """更新唤星服务器参数"""


class DeleteHuanxingServerParam(SchemaBase):
    """删除唤星服务器参数"""

    pks: list[int] = Field(description='唤星服务器 ID 列表')


class GetHuanxingServerDetail(HuanxingServerSchemaBase):
    """唤星服务器详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None


# ========== 新增：心跳、统计、看板 ==========


class HeartbeatParam(SchemaBase):
    """服务器心跳上报参数"""
    gateway_status: str = Field(description='Gateway状态: running/stopped/error')
    user_count: int = Field(0, description='本机用户总数')
    active_user_count: int = Field(0, description='本机活跃用户数')
    cpu_usage: float | None = Field(None, description='CPU使用率（百分比）')
    memory_usage: float | None = Field(None, description='内存使用率（百分比）')
    disk_usage: float | None = Field(None, description='磁盘使用率（百分比）')
    openclaw_version: str | None = Field(None, description='OpenClaw 版本')
    plugin_version: str | None = Field(None, description='huanxing-cloud 插件版本')


class HeartbeatResponse(SchemaBase):
    """心跳响应"""
    server_id: str
    received_at: datetime
    status: str = 'ok'


class ServerStatsResponse(SchemaBase):
    """服务器统计响应"""
    server_id: str
    server_name: str | None = None
    total_users: int = 0
    active_users: int = 0
    users_by_template: list[dict] = Field(default_factory=list, description='按模板分布')
    gateway_status: str | None = None
    last_heartbeat: datetime | None = None


class DashboardResponse(SchemaBase):
    """数据看板响应"""
    total_users: int = 0
    active_users: int = 0
    total_servers: int = 0
    active_servers: int = 0
    users_by_server: list[dict] = Field(default_factory=list, description='按服务器分布')
    users_by_template: list[dict] = Field(default_factory=list, description='按模板分布')


# ========== Agent 端 Schema ==========


class ServerChannelInfo(SchemaBase):
    """服务器渠道配置"""
    channel_type: str = Field(description='渠道类型: qqbot / onebot / feishu')
    bot_id: str | None = Field(None, description='机器人ID/QQ号')
    bot_name: str | None = Field(None, description='机器人名称')
    status: str = Field('active', description='渠道状态: active / disabled')


class AgentRegisterServerParam(SchemaBase):
    """Agent 注册/更新服务器参数"""
    server_id: str = Field(description='服务器唯一标识（如 huanxing-prod-01）')
    server_name: str | None = Field(None, description='服务器名称')
    ip_address: str | None = Field(None, description='服务器IP（不传则自动获取）')
    port: int | None = Field(None, description='SSH端口')
    region: str | None = Field(None, description='地域')
    provider: str | None = Field(None, description='云服务商')
    max_users: int | None = Field(None, description='最大用户容量')
    gateway_status: str | None = Field(None, description='Gateway状态')
    openclaw_version: str | None = Field(None, description='OpenClaw 版本')
    plugin_version: str | None = Field(None, description='插件版本')
    user_count: int = Field(0, description='当前用户总数')
    active_user_count: int = Field(0, description='活跃用户数')
    channels: list[ServerChannelInfo] | None = Field(None, description='服务器渠道配置列表')


class AgentRegisterServerResponse(SchemaBase):
    """Agent 注册服务器响应"""
    server_id: str
    is_new: bool = Field(description='是否新注册')
    status: str = 'ok'


class AgentHeartbeatParam(SchemaBase):
    """Agent 心跳上报参数"""
    gateway_status: str = Field(description='Gateway状态: running/stopped/error')
    user_count: int = Field(0, description='本机用户总数')
    active_user_count: int = Field(0, description='本机活跃用户数')
    cpu_usage: float | None = Field(None, description='CPU使用率（百分比）')
    memory_usage: float | None = Field(None, description='内存使用率（百分比）')
    disk_usage: float | None = Field(None, description='磁盘使用率（百分比）')
    openclaw_version: str | None = Field(None, description='OpenClaw 版本')
    plugin_version: str | None = Field(None, description='插件版本')
