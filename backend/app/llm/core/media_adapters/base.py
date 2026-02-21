"""媒体适配器抽象基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class MediaRequest:
    """统一媒体生成请求"""

    prompt: str
    model: str
    # 图像参数
    n: int = 1
    size: str = '1024x1024'
    quality: str | None = None
    style: str | None = None
    # 视频参数
    duration: int | None = None
    aspect_ratio: str | None = None
    mode: str | None = None
    cfg_scale: float | None = None
    image_url: str | None = None
    # 通用
    webhook_url: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class SubmitResult:
    """适配器提交结果"""

    vendor_task_id: str | None = None
    vendor_urls: list[str] | None = None
    is_async: bool = False
    estimated_seconds: int | None = None
    revised_prompt: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class PollResult:
    """适配器轮询结果"""

    status: str = 'processing'  # processing / completed / failed
    progress: int = 0
    vendor_urls: list[str] | None = None
    error_code: str | None = None
    error_message: str | None = None
    duration: float | None = None
    resolution: str | None = None
    extra: dict = field(default_factory=dict)


class MediaAdapter(ABC):
    """媒体生成适配器抽象基类"""

    provider_type: str  # 对应 ProviderType 枚举值
    media_type: str     # "image" | "video"

    def __init__(self, api_base_url: str | None = None, api_key: str | None = None) -> None:
        self.api_base_url = api_base_url
        self.api_key = api_key

    @abstractmethod
    async def submit(self, request: MediaRequest) -> SubmitResult:
        """提交生成任务，返回厂商任务 ID 或直接结果"""

    @abstractmethod
    async def poll(self, vendor_task_id: str) -> PollResult:
        """查询任务状态，返回进度或结果 URL"""

    def normalize_params(self, request: MediaRequest) -> dict:
        """将统一参数转换为厂商特定参数（子类可覆盖）"""
        return {}

    def estimate_credits(self, request: MediaRequest, cost_per_generation: Decimal | None = None, cost_per_second: Decimal | None = None) -> Decimal:
        """预估积分消耗"""
        if self.media_type == 'video' and cost_per_second and request.duration:
            return cost_per_second * Decimal(str(request.duration))
        if cost_per_generation:
            return cost_per_generation * Decimal(str(request.n))
        return Decimal('1')
