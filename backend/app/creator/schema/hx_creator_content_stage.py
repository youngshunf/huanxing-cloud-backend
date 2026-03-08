from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorContentStageSchemaBase(SchemaBase):
    """内容阶段产出基础模型"""
    content_id: int = Field(description='关联内容ID')
    user_id: int = Field(description='关联用户ID')
    stage: str = Field(description='阶段：research/outline/first_draft/final_draft/cover/video_script')
    content_text: str | None = Field(None, description='产出内容文本')
    file_url: str | None = Field(None, description='产出文件URL（图片/视频）')
    status: str | None = Field(None, description='状态：draft/approved/archived')
    version: int | None = Field(None, description='版本号')
    source_type: str | None = Field(None, description='来源：ai_generated/human_edited/imported')
    meta_data: dict | None = Field(None, description='扩展信息JSON')


class CreateHxCreatorContentStageParam(HxCreatorContentStageSchemaBase):
    """创建内容阶段产出参数"""


class UpdateHxCreatorContentStageParam(HxCreatorContentStageSchemaBase):
    """更新内容阶段产出参数"""


class DeleteHxCreatorContentStageParam(SchemaBase):
    """删除内容阶段产出参数"""

    pks: list[int] = Field(description='内容阶段产出 ID 列表')


class GetHxCreatorContentStageDetail(HxCreatorContentStageSchemaBase):
    """内容阶段产出详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
