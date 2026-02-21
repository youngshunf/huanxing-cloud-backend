"""适配器注册表"""

from typing import TYPE_CHECKING

from backend.common.exception.errors import HTTPError

if TYPE_CHECKING:
    from backend.app.llm.core.media_adapters.base import MediaAdapter


class UnsupportedAdapterError(HTTPError):
    """不支持的适配器"""

    def __init__(self, key: str) -> None:
        super().__init__(code=400, msg=f'不支持的媒体适配器: {key}')


ADAPTER_REGISTRY: dict[str, type['MediaAdapter']] = {}


def register_adapter(provider: str, media_type: str):
    """适配器注册装饰器

    用法：
        @register_adapter("openai", "image")
        class OpenAIImageAdapter(MediaAdapter):
            ...
    """

    def decorator(cls: type['MediaAdapter']) -> type['MediaAdapter']:
        key = f'{provider}:{media_type}'
        ADAPTER_REGISTRY[key] = cls
        return cls

    return decorator


def get_adapter(
    provider: str,
    media_type: str,
    *,
    api_base_url: str | None = None,
    api_key: str | None = None,
) -> 'MediaAdapter':
    """获取适配器实例"""
    key = f'{provider}:{media_type}'
    cls = ADAPTER_REGISTRY.get(key)
    if not cls:
        raise UnsupportedAdapterError(key)
    return cls(api_base_url=api_base_url, api_key=api_key)
