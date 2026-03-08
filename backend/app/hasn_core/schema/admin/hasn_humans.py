"""HASN 用户管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnHumanSchemaBase(SchemaBase):
    """用户基础 Schema"""
    star_id: str = Field(description='唤星号')
    name: str = Field(description='用户名')
    huanxing_user_id: str | None = Field(None, description='唤星平台用户ID')
    bio: str | None = Field(None, description='个人简介')
    avatar_url: str | None = Field(None, description='头像URL')
    phone: str | None = Field(None, description='手机号(加密)')
    phone_hash: str | None = Field(None, description='手机号哈希')
    profile: dict | None = Field(None, description='扩展资料(JSON)')
    privacy_rules: dict | None = Field(None, description='隐私规则(JSON)')
    status: str | None = Field(None, description='状态')
    last_online_at: datetime | None = Field(None, description='最后在线时间')


class CreateHasnHumanParam(HasnHumanSchemaBase):
    """创建用户参数"""


class UpdateHasnHumanParam(HasnHumanSchemaBase):
    """更新用户参数"""


class DeleteHasnHumanParam(SchemaBase):
    """删除用户参数"""
    pks: list[str] = Field(description='用户 ID 列表')


class GetHasnHumanDetail(HasnHumanSchemaBase):
    """用户详情"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_time: datetime
    updated_time: datetime | None = None
