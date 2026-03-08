from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorDraftSchemaBase(SchemaBase):
    """草稿箱基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    title: str | None = Field(None, description='标题')
    content: str = Field(description='内容')
    media: dict | None = Field(None, description='媒体文件JSON数组')
    tags: dict | None = Field(None, description='标签JSON数组')
    target_platforms: dict | None = Field(None, description='目标平台JSON数组')
    meta_data: dict | None = Field(None, description='扩展信息JSON')


class CreateHxCreatorDraftParam(HxCreatorDraftSchemaBase):
    """创建草稿箱参数"""


class UpdateHxCreatorDraftParam(HxCreatorDraftSchemaBase):
    """更新草稿箱参数"""


class DeleteHxCreatorDraftParam(SchemaBase):
    """删除草稿箱参数"""

    pks: list[int] = Field(description='草稿箱 ID 列表')


class GetHxCreatorDraftDetail(HxCreatorDraftSchemaBase):
    """草稿箱详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
