"""通义万相图像生成适配器"""

import httpx

from backend.app.llm.core.media_adapters.base import MediaAdapter, MediaRequest, PollResult, SubmitResult
from backend.app.llm.core.media_adapters.registry import register_adapter
from backend.app.llm.enums import MediaErrorCode
from backend.common.log import log

# 通义万相 API 地址
DASHSCOPE_API_BASE = 'https://dashscope.aliyuncs.com/api/v1'

# 错误映射
DASHSCOPE_ERROR_MAP = {
    'DataInspectionFailed': MediaErrorCode.CONTENT_POLICY,
    'Throttling': MediaErrorCode.RATE_LIMITED,
    'Throttling.RateQuota': MediaErrorCode.RATE_LIMITED,
    'InvalidParameter': MediaErrorCode.INVALID_PARAMS,
    'InvalidApiKey': MediaErrorCode.MODEL_UNAVAILABLE,
}


@register_adapter('qwen', 'image')
class DashScopeImageAdapter(MediaAdapter):
    """通义万相图像生成（异步轮询）"""

    provider_type = 'qwen'
    media_type = 'image'

    def normalize_params(self, request: MediaRequest) -> dict:
        w, h = request.size.split('x')
        return {
            'model': request.model or 'wanx-v1',
            'input': {'prompt': request.prompt},
            'parameters': {
                'size': f'{w}*{h}',
                'n': request.n,
                'style': request.style or '<auto>',
            },
        }

    async def submit(self, request: MediaRequest) -> SubmitResult:
        """提交异步生成任务"""
        params = self.normalize_params(request)
        url = f'{self.api_base_url or DASHSCOPE_API_BASE}/services/aigc/text2image/image-synthesis'

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    url,
                    json=params,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json',
                        'X-DashScope-Async': 'enable',
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                output = data.get('output', {})
                task_id = output.get('task_id')

                if not task_id:
                    raise DashScopeImageError(
                        MediaErrorCode.VENDOR_ERROR,
                        f'未返回 task_id: {data}',
                    )

                log.info(f'[DashScope Image] 任务已提交: {task_id}')
                return SubmitResult(
                    vendor_task_id=task_id,
                    is_async=True,
                    estimated_seconds=30,
                )
            except httpx.HTTPStatusError as e:
                error_body = e.response.json() if e.response.content else {}
                error_code = error_body.get('code', '')
                error_message = error_body.get('message', str(e))
                mapped_code = DASHSCOPE_ERROR_MAP.get(error_code, MediaErrorCode.VENDOR_ERROR)
                log.error(f'[DashScope Image] 提交失败: {error_code} - {error_message}')
                raise DashScopeImageError(mapped_code, error_message) from e

    async def poll(self, vendor_task_id: str) -> PollResult:
        """轮询任务状态"""
        url = f'{self.api_base_url or DASHSCOPE_API_BASE}/tasks/{vendor_task_id}'

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(
                    url,
                    headers={'Authorization': f'Bearer {self.api_key}'},
                )
                resp.raise_for_status()
                data = resp.json()

                output = data.get('output', {})
                task_status = output.get('task_status', '')

                if task_status == 'SUCCEEDED':
                    results = output.get('results', [])
                    urls = [r['url'] for r in results if r.get('url')]
                    log.info(f'[DashScope Image] 任务完成: {vendor_task_id}, {len(urls)} 张图片')
                    return PollResult(status='completed', progress=100, vendor_urls=urls)

                if task_status == 'FAILED':
                    error_code = output.get('code', '')
                    error_message = output.get('message', '生成失败')
                    mapped_code = DASHSCOPE_ERROR_MAP.get(error_code, MediaErrorCode.VENDOR_ERROR)
                    log.error(f'[DashScope Image] 任务失败: {vendor_task_id} - {error_message}')
                    return PollResult(
                        status='failed',
                        error_code=mapped_code,
                        error_message=error_message,
                    )

                # PENDING / RUNNING
                metrics = output.get('task_metrics', {})
                total = metrics.get('TOTAL', 1)
                succeeded = metrics.get('SUCCEEDED', 0)
                progress = int(succeeded / total * 100) if total > 0 else 0
                return PollResult(status='processing', progress=progress)

            except httpx.HTTPStatusError as e:
                log.error(f'[DashScope Image] 轮询失败: {vendor_task_id} - {e}')
                return PollResult(
                    status='failed',
                    error_code=MediaErrorCode.VENDOR_ERROR,
                    error_message=str(e),
                )


class DashScopeImageError(Exception):
    """通义万相错误"""

    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(message)
