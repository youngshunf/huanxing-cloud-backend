"""视频生成 Schema"""

from pydantic import Field

from backend.common.schema import SchemaBase


class VideoGenerationRequest(SchemaBase):
    """视频生成请求"""

    model: str = Field(description='模型名称')
    prompt: str = Field(description='生成提示词')
    duration: int = Field(default=5, ge=1, le=60, description='视频时长(秒)')
    aspect_ratio: str = Field(default='16:9', description='宽高比')
    mode: str | None = Field(default=None, description='生成模式 (std/pro)')
    cfg_scale: float | None = Field(default=None, description='创意度')
    image_url: str | None = Field(default=None, description='参考图片 URL')
    webhook_url: str | None = Field(default=None, description='Webhook 回调 URL')


class VideoDataItem(SchemaBase):
    """视频数据项"""

    url: str | None = None
    duration: float | None = None
    resolution: str | None = None


class VideoUsage(SchemaBase):
    """视频用量"""

    credits: float


class VideoGenerationResponse(SchemaBase):
    """视频生成响应"""

    id: str
    status: str
    progress: int | None = None
    estimated_seconds: int | None = None
    data: VideoDataItem | None = None
    usage: VideoUsage | None = None
    created: int
    error: dict | None = None
