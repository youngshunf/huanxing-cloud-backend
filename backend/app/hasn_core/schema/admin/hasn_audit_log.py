"""HASN 审计日志管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnAuditLogSchemaBase(SchemaBase):
    """审计日志基础 Schema"""
    actor_id: str = Field(description='操作者hasn_id')
    actor_type: str = Field(description='操作者类型')
    action: str = Field(description='操作')
    target_type: str | None = Field(None, description='目标类型')
    target_id: str | None = Field(None, description='目标ID')
    details: dict | None = Field(None, description='详情(JSON)')
    ip_address: str | None = Field(None, description='IP地址')


class CreateHasnAuditLogParam(HasnAuditLogSchemaBase):
    """创建审计日志参数"""


class UpdateHasnAuditLogParam(HasnAuditLogSchemaBase):
    """更新审计日志参数"""


class DeleteHasnAuditLogParam(SchemaBase):
    """删除审计日志参数"""
    pks: list[int] = Field(description='审计日志 ID 列表')


class GetHasnAuditLogDetail(HasnAuditLogSchemaBase):
    """审计日志详情"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
