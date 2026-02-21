"""媒体生成适配器"""

from backend.app.llm.core.media_adapters.base import MediaAdapter, MediaRequest, PollResult, SubmitResult
from backend.app.llm.core.media_adapters.registry import ADAPTER_REGISTRY, get_adapter, register_adapter

# 导入具体适配器以触发 @register_adapter 注册
from backend.app.llm.core.media_adapters.dashscope_image import DashScopeImageAdapter  # noqa: F401
from backend.app.llm.core.media_adapters.kling_video import KlingVideoAdapter  # noqa: F401
from backend.app.llm.core.media_adapters.openai_image import OpenAIImageAdapter  # noqa: F401

__all__ = [
    'ADAPTER_REGISTRY',
    'MediaAdapter',
    'MediaRequest',
    'PollResult',
    'SubmitResult',
    'get_adapter',
    'register_adapter',
]
