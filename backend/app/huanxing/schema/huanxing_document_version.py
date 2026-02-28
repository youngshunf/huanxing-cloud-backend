from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HuanxingDocumentVersionSchemaBase(SchemaBase):
    """文档版本历史基础模型"""
    document_id: int = Field(description='文档ID')
    version_number: int = Field(description='版本号')
    title: str = Field(description='文档标题')
    content: str = Field(description='Markdown内容')
    created_by: int = Field(description='创建者用户ID')
    created_at: datetime = Field(description='创建时间')


class CreateHuanxingDocumentVersionParam(HuanxingDocumentVersionSchemaBase):
    """创建文档版本历史参数"""


class UpdateHuanxingDocumentVersionParam(HuanxingDocumentVersionSchemaBase):
    """更新文档版本历史参数"""


class DeleteHuanxingDocumentVersionParam(SchemaBase):
    """删除文档版本历史参数"""

    pks: list[int] = Field(description='文档版本历史 ID 列表')


class GetHuanxingDocumentVersionDetail(HuanxingDocumentVersionSchemaBase):
    """文档版本历史详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
