"""图像生成 Schema"""

from pydantic import Field

from backend.common.schema import SchemaBase


class ImageGenerationRequest(SchemaBase):
    """图像生成请求 — OpenAI 兼容"""

    model: str = Field(description='模型名称')
    prompt: str = Field(description='生成提示词')
    n: int = Field(default=1, ge=1, le=10, description='生成数量')
    size: str = Field(default='1024x1024', description='图像尺寸')
    quality: str | None = Field(default=None, description='质量 (hd/standard)')
    style: str | None = Field(default=None, description='风格')
    response_format: str = Field(default='url', description='响应格式 (url/b64_json)')
    webhook_url: str | None = Field(default=None, description='Webhook 回调 URL')


class ImageDataItem(SchemaBase):
    """图像数据项"""

    url: str | None = None
    b64_json: str | None = None
    revised_prompt: str | None = None


class ImageUsage(SchemaBase):
    """图像用量"""

    credits: float


class ImageGenerationResponse(SchemaBase):
    """图像生成响应"""

    id: str
    status: str = 'completed'
    data: list[ImageDataItem] | None = None
    usage: ImageUsage | None = None
    created: int
    # 异步任务字段
    progress: int | None = None
    error: dict | None = None
