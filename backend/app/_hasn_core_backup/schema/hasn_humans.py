from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnHumansSchemaBase(SchemaBase):
    """HASN 人类用户身份基础模型"""
    hasn_id: str = Field(description='HASN 唯一标识 (h_{uuid})')
    star_id: str = Field(description='唤星号 (数字号或自定义号)')
    user_id: int = Field(description='关联唤星平台用户 ID')
    name: str = Field(description='显示名称')
    bio: str | None = Field(None, description='个人简介')
    avatar_url: str | None = Field(None, description='头像 URL')
    status: str = Field(default='active', description='状态: active/suspended/deleted')
    contact_policy: dict = Field(default_factory=dict, description='联系人策略')
    timezone: str | None = Field(default='Asia/Shanghai', description='时区')
    tags: list[str] | None = Field(None, description='个人标签')
    stats: dict = Field(default_factory=dict, description='统计信息')


class CreateHasnHumansParam(HasnHumansSchemaBase):
    """创建 HASN 人类用户参数"""


class UpdateHasnHumansParam(SchemaBase):
    """更新 HASN 人类用户参数"""
    name: str | None = Field(None, description='显示名称')
    bio: str | None = Field(None, description='个人简介')
    avatar_url: str | None = Field(None, description='头像 URL')
    contact_policy: dict | None = Field(None, description='联系人策略')
    timezone: str | None = Field(None, description='时区')
    tags: list[str] | None = Field(None, description='个人标签')


class DeleteHasnHumansParam(SchemaBase):
    """删除 HASN 人类用户参数"""
    pks: list[int] = Field(description='HASN 人类用户 ID 列表')


class GetHasnHumansDetail(HasnHumansSchemaBase):
    """HASN 人类用户详情"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
