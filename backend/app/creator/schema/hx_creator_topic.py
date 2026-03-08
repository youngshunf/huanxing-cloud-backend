from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorTopicSchemaBase(SchemaBase):
    """选题推荐基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    title: str = Field(description='选题标题')
    potential_score: float | None = Field(None, description='潜力评分')
    heat_index: float | None = Field(None, description='热度指数')
    reason: str | None = Field(None, description='推荐理由')
    keywords: dict | None = Field(None, description='关键词JSON数组')
    creative_angles: dict | None = Field(None, description='创作角度JSON')
    status: int = Field(description='状态：0-待处理 1-已采纳 2-已跳过')
    content_id: int | None = Field(None, description='采纳后关联的内容ID')
    batch_date: str | None = Field(None, description='批次日期')
    source_uid: str | None = Field(None, description='来源标识')


class CreateHxCreatorTopicParam(HxCreatorTopicSchemaBase):
    """创建选题推荐参数"""


class UpdateHxCreatorTopicParam(HxCreatorTopicSchemaBase):
    """更新选题推荐参数"""


class DeleteHxCreatorTopicParam(SchemaBase):
    """删除选题推荐参数"""

    pks: list[int] = Field(description='选题推荐 ID 列表')


class GetHxCreatorTopicDetail(HxCreatorTopicSchemaBase):
    """选题推荐详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
