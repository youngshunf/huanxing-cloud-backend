from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppScopesSchemaBase(SchemaBase):
    """应用权限定义表（{domain}.* namespace）基础模型"""
    app_id: str = Field(description='关联的 App ID')
    scope: str = Field(description='权限标识，格式：{domain}.{resource}.{action}')
    display_name: str = Field(description='权限显示名称')
    description: str = Field(description='权限描述')
    reason: str | None = Field(None, description='为什么需要这个权限')
    risk_level: str = Field(description='风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)')
    requires_owner_confirmation: bool | None = Field(None, description='是否需要 Owner 二次确认')
    rate_limit_per_minute: int | None = Field(None, description='每分钟限流次数')
    rate_limit_per_hour: int | None = Field(None, description='每小时限流次数')
    rate_limit_per_day: int | None = Field(None, description='每天限流次数')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime = Field(description='更新时间')


class CreateAppScopesParam(AppScopesSchemaBase):
    """创建应用权限定义表（{domain}.* namespace）参数"""


class UpdateAppScopesParam(AppScopesSchemaBase):
    """更新应用权限定义表（{domain}.* namespace）参数"""


class DeleteAppScopesParam(SchemaBase):
    """删除应用权限定义表（{domain}.* namespace）参数"""

    pks: list[int] = Field(description='应用权限定义表（{domain}.* namespace） ID 列表')


class GetAppScopesDetail(AppScopesSchemaBase):
    """应用权限定义表（{domain}.* namespace）详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
