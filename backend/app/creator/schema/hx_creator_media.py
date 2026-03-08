from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorMediaSchemaBase(SchemaBase):
    """素材库基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    type: str = Field(description='类型：image/video/audio/template')
    url: str = Field(description='文件URL')
    filename: str = Field(description='文件名')
    size: int | None = Field(None, description='文件大小（字节）')
    width: int | None = Field(None, description='宽度（像素）')
    height: int | None = Field(None, description='高度（像素）')
    duration: int | None = Field(None, description='时长（秒）')
    thumbnail_url: str | None = Field(None, description='缩略图URL')
    tags: dict | None = Field(None, description='标签JSON数组')
    description: str | None = Field(None, description='描述')


class CreateHxCreatorMediaParam(HxCreatorMediaSchemaBase):
    """创建素材库参数"""


class UpdateHxCreatorMediaParam(HxCreatorMediaSchemaBase):
    """更新素材库参数"""


class DeleteHxCreatorMediaParam(SchemaBase):
    """删除素材库参数"""

    pks: list[int] = Field(description='素材库 ID 列表')


class GetHxCreatorMediaDetail(HxCreatorMediaSchemaBase):
    """素材库详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
