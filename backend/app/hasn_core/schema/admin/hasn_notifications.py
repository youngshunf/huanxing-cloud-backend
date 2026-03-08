"""HASN 通知管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnNotificationSchemaBase(SchemaBase):
    """通知基础 Schema"""
    target_id: str = Field(description='目标hasn_id')
    type: str = Field(description='通知类型')
    title: str = Field(description='标题')
    body: str | None = Field(None, description='正文')
    data: dict | None = Field(None, description='附加数据(JSON)')
    read: bool | None = Field(None, description='是否已读')


class CreateHasnNotificationParam(HasnNotificationSchemaBase):
    """创建通知参数"""


class UpdateHasnNotificationParam(HasnNotificationSchemaBase):
    """更新通知参数"""


class DeleteHasnNotificationParam(SchemaBase):
    """删除通知参数"""
    pks: list[int] = Field(description='通知 ID 列表')


class GetHasnNotificationDetail(HasnNotificationSchemaBase):
    """通知详情"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
