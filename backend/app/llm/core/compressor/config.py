"""上下文压缩配置
@author Guardian
"""

from dataclasses import dataclass


@dataclass
class CompressConfig:
    """上下文压缩配置"""

    # ---- 全局开关 ----
    enabled: bool = True

    # ---- 触发条件 ----
    # 当估算 token 超过模型 max_context 的此比例时触发压缩
    token_threshold_ratio: float = 0.75
    # 消息数阈值（与 token 阈值取 OR）
    message_threshold: int = 100

    # ---- 保留策略 ----
    # 保留最近 N 条消息不压缩
    keep_message_count: int = 6
    # 工具调用配对保护：最大回溯距离
    max_tool_lookback: int = 10

    # ---- 摘要生成 ----
    summary_model: str = 'claude-sonnet-4-5-20250929'
    max_batch_chars: int = 80000
    max_summary_tokens: int = 25000
    summary_timeout: int = 60

    # ---- 缓存 ----
    cache_enabled: bool = True
    cache_prefix: str = 'hx:llm:compress'
    cache_ttl: int = 86400  # 24h

    # ---- 二次压缩与降级 ----
    # 压缩后仍超限时，尝试合并所有摘要块为一个精简摘要
    enable_secondary_compression: bool = True
    # 降级保留消息数序列（依次尝试，直到不超限）
    degraded_keep_counts: tuple[int, ...] = (4, 2)
    # 摘要生成最大重试次数
    summary_max_retries: int = 1

    # ---- 工具结果裁剪 ----
    max_tool_result_length: int = 2000
    keep_head_chars: int = 800
    keep_tail_chars: int = 800


def load_compress_config() -> CompressConfig:
    """从 settings 加载压缩配置"""
    from backend.core.conf import settings

    return CompressConfig(
        enabled=getattr(settings, 'LLM_COMPRESS_ENABLED', True),
        token_threshold_ratio=getattr(settings, 'LLM_COMPRESS_THRESHOLD_RATIO', 0.75),
        message_threshold=getattr(settings, 'LLM_COMPRESS_MESSAGE_THRESHOLD', 100),
        keep_message_count=getattr(settings, 'LLM_COMPRESS_KEEP_MESSAGES', 6),
        summary_model=getattr(settings, 'LLM_COMPRESS_SUMMARY_MODEL', 'claude-sonnet-4-5-20250929'),
        cache_ttl=getattr(settings, 'LLM_COMPRESS_CACHE_TTL', 86400),
    )


def is_compress_enabled(
    global_config: CompressConfig,
    api_key_metadata: dict | None,
) -> bool:
    """
    判断是否启用压缩（API Key 级别 > 全局级别）

    三态逻辑：
    - API Key metadata 中 compress_enabled=true  → 开启
    - API Key metadata 中 compress_enabled=false → 关闭
    - 无此字段 / metadata 为 None → 跟随全局配置
    """
    if api_key_metadata and 'compress_enabled' in api_key_metadata:
        return bool(api_key_metadata['compress_enabled'])
    return global_config.enabled


def get_threshold_ratio(
    global_config: CompressConfig,
    api_key_metadata: dict | None,
) -> float:
    """获取压缩阈值比例（API Key 可覆盖全局）"""
    if api_key_metadata and 'compress_threshold_ratio' in api_key_metadata:
        try:
            return float(api_key_metadata['compress_threshold_ratio'])
        except (ValueError, TypeError):
            pass
    return global_config.token_threshold_ratio
