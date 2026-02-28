from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HuanxingDocumentAutosaveSchemaBase(SchemaBase):
    """文档自动保存表（每文档每用户仅一条，UPSERT更新）基础模型"""
    document_id: int = Field(description='文档ID')
    user_id: int = Field(description='用户ID')
    content: str = Field(description='Markdown内容')
    saved_at: datetime = Field(description='最后保存时间')


class CreateHuanxingDocumentAutosaveParam(HuanxingDocumentAutosaveSchemaBase):
    """创建文档自动保存表（每文档每用户仅一条，UPSERT更新）参数"""


class UpdateHuanxingDocumentAutosaveParam(HuanxingDocumentAutosaveSchemaBase):
    """更新文档自动保存表（每文档每用户仅一条，UPSERT更新）参数"""


class DeleteHuanxingDocumentAutosaveParam(SchemaBase):
    """删除文档自动保存表（每文档每用户仅一条，UPSERT更新）参数"""

    pks: list[int] = Field(description='文档自动保存表（每文档每用户仅一条，UPSERT更新） ID 列表')


class GetHuanxingDocumentAutosaveDetail(HuanxingDocumentAutosaveSchemaBase):
    """文档自动保存表（每文档每用户仅一条，UPSERT更新）详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
