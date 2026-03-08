"""HASN 联系人管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnContactSchemaBase(SchemaBase):
    """联系人基础 Schema"""
    owner_id: str = Field(description='拥有者hasn_id')
    peer_id: str = Field(description='对方hasn_id')
    peer_type: str = Field(description='对方类型(human/agent)')
    relation_type: str | None = Field(None, description='关系类型')
    trust_level: int | None = Field(None, description='信任等级(0-4)')
    scope: dict | None = Field(None, description='关系作用域(JSON)')
    custom_permissions: dict | None = Field(None, description='自定义权限(JSON)')
    nickname: str | None = Field(None, description='备注名')
    tags: list[str] | None = Field(None, description='标签')
    subscription: bool | None = Field(None, description='是否订阅')
    status: str | None = Field(None, description='状态')
    request_message: str | None = Field(None, description='好友请求附言')
    auto_expire: datetime | None = Field(None, description='自动过期时间')
    interaction_count: int | None = Field(None, description='互动次数')


class CreateHasnContactParam(HasnContactSchemaBase):
    """创建联系人参数"""


class UpdateHasnContactParam(HasnContactSchemaBase):
    """更新联系人参数"""


class DeleteHasnContactParam(SchemaBase):
    """删除联系人参数"""
    pks: list[int] = Field(description='联系人 ID 列表')


class GetHasnContactDetail(HasnContactSchemaBase):
    """联系人详情"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
