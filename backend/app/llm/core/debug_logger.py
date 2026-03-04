"""
LLM Gateway Debug Logger

debug 模式下将每次 LLM 请求和响应的完整数据写入独立日志文件。
日志文件按天轮转，保留 7 天，单文件最大 200MB。

使用方式：
    from backend.app.llm.core.debug_logger import llm_debug_log
    llm_debug_log.log_request(request_id, params)
    llm_debug_log.log_response(request_id, response, elapsed_ms)
    llm_debug_log.log_error(request_id, error)
    llm_debug_log.log_stream_chunk(request_id, chunk)  # 流式片段
"""

import json
import os
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from loguru import logger

from backend.core.path_conf import LOG_DIR

# LLM debug 日志目录
LLM_DEBUG_LOG_DIR = LOG_DIR / 'llm_debug'


class _JSONEncoder(json.JSONEncoder):
    """处理特殊类型的 JSON 序列化"""

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, bytes):
            return o.decode('utf-8', errors='replace')
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, 'model_dump'):
            return o.model_dump(exclude_none=True)
        if hasattr(o, '__dict__'):
            return {k: v for k, v in o.__dict__.items() if not k.startswith('_')}
        return str(o)


def _safe_json(data: Any, max_length: int = 0) -> str:
    """安全地将数据序列化为 JSON 字符串"""
    try:
        text = json.dumps(data, cls=_JSONEncoder, ensure_ascii=False, indent=2)
        if max_length and len(text) > max_length:
            return text[:max_length] + f'\n... (truncated, total {len(text)} chars)'
        return text
    except Exception as e:
        return f'<serialization error: {e}>\n{repr(data)[:2000]}'


def _mask_api_key(params: dict) -> dict:
    """隐藏 API Key"""
    safe = params.copy()
    if 'api_key' in safe and safe['api_key']:
        key = safe['api_key']
        safe['api_key'] = f'{key[:8]}...{key[-4:]}' if len(key) > 12 else '***'
    return safe


class LLMDebugLogger:
    """LLM 调试日志记录器"""

    def __init__(self) -> None:
        self._logger = None
        self._enabled: bool | None = None

    @property
    def enabled(self) -> bool:
        if self._enabled is None:
            from backend.core.conf import settings
            self._enabled = getattr(settings, 'LITELLM_DEBUG', False)
        return self._enabled

    def _get_logger(self):
        """延迟初始化独立的 loguru logger"""
        if self._logger is None:
            if not os.path.exists(LLM_DEBUG_LOG_DIR):
                os.makedirs(LLM_DEBUG_LOG_DIR, exist_ok=True)

            self._logger = logger.bind(llm_debug=True)

            # 添加独立的 sink，不影响主日志
            logger.add(
                str(LLM_DEBUG_LOG_DIR / 'llm_debug_{time:YYYY-MM-DD}.log'),
                level='TRACE',
                filter=lambda record: record.get('extra', {}).get('llm_debug', False),
                format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}',
                rotation='00:00',       # 每天轮转
                retention='7 days',     # 保留 7 天
                compression='gz',       # 压缩旧日志
                enqueue=True,           # 异步写入，不阻塞主线程
                serialize=False,
                encoding='utf-8',
            )

        return self._logger

    def info(self, message: str) -> None:
        """写入 info 级别的调试信息到日志文件（不输出到控制台）"""
        if not self.enabled:
            return
        self._get_logger().info(message)

    def error(self, message: str) -> None:
        """写入 error 级别的调试信息到日志文件（不输出到控制台）"""
        if not self.enabled:
            return
        self._get_logger().error(message)

    def log_request(
        self,
        request_id: str,
        params: dict[str, Any],
        *,
        provider_name: str = '',
        model_name: str = '',
        api_base: str = '',
        is_streaming: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """记录完整的 LLM 请求"""
        if not self.enabled:
            return

        safe_params = _mask_api_key(params)

        record = {
            'event': 'REQUEST',
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'provider': provider_name,
            'model': model_name,
            'api_base': api_base,
            'streaming': is_streaming,
            'params': safe_params,
        }
        if extra:
            record['extra'] = extra

        self._get_logger().info(
            f'[REQUEST] {request_id} | {provider_name}/{model_name} | stream={is_streaming}\n'
            f'{_safe_json(record)}'
        )

    def log_response(
        self,
        request_id: str,
        response: Any,
        *,
        elapsed_ms: int = 0,
        provider_name: str = '',
        model_name: str = '',
        input_tokens: int = 0,
        output_tokens: int = 0,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """记录完整的 LLM 响应"""
        if not self.enabled:
            return

        # 尝试提取响应数据
        if hasattr(response, 'model_dump'):
            response_data = response.model_dump(exclude_none=True)
        elif hasattr(response, 'dict'):
            response_data = response.dict()
        elif isinstance(response, dict):
            response_data = response
        else:
            response_data = str(response)

        record = {
            'event': 'RESPONSE',
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'provider': provider_name,
            'model': model_name,
            'elapsed_ms': elapsed_ms,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'response': response_data,
        }
        if extra:
            record['extra'] = extra

        self._get_logger().info(
            f'[RESPONSE] {request_id} | {provider_name}/{model_name} | '
            f'{elapsed_ms}ms | tokens: in={input_tokens} out={output_tokens}\n'
            f'{_safe_json(record)}'
        )

    def log_stream_end(
        self,
        request_id: str,
        *,
        elapsed_ms: int = 0,
        provider_name: str = '',
        model_name: str = '',
        input_tokens: int = 0,
        output_tokens: int = 0,
        chunk_count: int = 0,
        full_content: str = '',
    ) -> None:
        """记录流式响应结束（汇总）"""
        if not self.enabled:
            return

        record = {
            'event': 'STREAM_END',
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'provider': provider_name,
            'model': model_name,
            'elapsed_ms': elapsed_ms,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'chunk_count': chunk_count,
            'full_content': full_content,
        }

        self._get_logger().info(
            f'[STREAM_END] {request_id} | {provider_name}/{model_name} | '
            f'{elapsed_ms}ms | tokens: in={input_tokens} out={output_tokens} | chunks: {chunk_count}\n'
            f'{_safe_json(record)}'
        )

    def log_error(
        self,
        request_id: str,
        error: Exception | str,
        *,
        provider_name: str = '',
        model_name: str = '',
        elapsed_ms: int = 0,
    ) -> None:
        """记录 LLM 调用错误"""
        if not self.enabled:
            return

        import traceback

        if isinstance(error, Exception):
            error_type = type(error).__name__
            error_message = str(error)
            error_traceback = traceback.format_exception(type(error), error, error.__traceback__)
        else:
            error_type = 'str'
            error_message = error
            error_traceback = None

        record = {
            'event': 'ERROR',
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'provider': provider_name,
            'model': model_name,
            'elapsed_ms': elapsed_ms,
            'error_type': error_type,
            'error_message': error_message,
        }
        if error_traceback:
            record['traceback'] = ''.join(error_traceback)

        self._get_logger().error(
            f'[ERROR] {request_id} | {provider_name}/{model_name} | '
            f'{error_type}: {error_message[:200]}\n'
            f'{_safe_json(record)}'
        )


# 全局单例
llm_debug_log = LLMDebugLogger()
