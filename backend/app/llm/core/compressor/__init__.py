"""智能上下文压缩器
@author Guardian

在 LLM 网关层透明地压缩长对话历史，对客户端无感。
"""

from .compressor import CompressResult, ContextCompressor
from .config import CompressConfig, is_compress_enabled, load_compress_config

__all__ = [
    'CompressConfig',
    'CompressResult',
    'ContextCompressor',
    'context_compressor',
    'is_compress_enabled',
]

# 延迟初始化单例（避免 import 时触发 settings 加载）
_instance: ContextCompressor | None = None


def get_compressor() -> ContextCompressor:
    """获取压缩器单例（延迟初始化）"""
    global _instance
    if _instance is None:
        config = load_compress_config()
        _instance = ContextCompressor(config)
    return _instance


class _CompressorProxy:
    """压缩器代理，支持属性访问的延迟初始化"""

    def __getattr__(self, name):
        return getattr(get_compressor(), name)


context_compressor: ContextCompressor = _CompressorProxy()  # type: ignore[assignment]
