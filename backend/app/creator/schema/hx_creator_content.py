from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorContentSchemaBase(SchemaBase):
    """内容创作主基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    title: str | None = Field(None, description='内容标题')
    status: str = Field(description='状态：idea/researching/drafting/reviewing/ready/published/analyzing/completed/archived')
    target_platforms: dict | None = Field(None, description='目标平台JSON数组')
    pipeline_mode: str | None = Field(None, description='流水线模式：manual/semi-auto/auto')
    content_tracks: str | None = Field(None, description='创作轨道：article/video/article,video')
    viral_pattern_id: int | None = Field(None, description='使用的爆款模式ID')
    meta_data: dict | None = Field(None, description='扩展信息JSON')


class CreateHxCreatorContentParam(HxCreatorContentSchemaBase):
    """创建内容创作主参数"""


class UpdateHxCreatorContentParam(HxCreatorContentSchemaBase):
    """更新内容创作主参数"""


class DeleteHxCreatorContentParam(SchemaBase):
    """删除内容创作主参数"""

    pks: list[int] = Field(description='内容创作主 ID 列表')


class GetHxCreatorContentDetail(HxCreatorContentSchemaBase):
    """内容创作主详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
