"""DALL-E 3 图像生成适配器"""

import httpx

from backend.app.llm.core.media_adapters.base import MediaAdapter, MediaRequest, PollResult, SubmitResult
from backend.app.llm.core.media_adapters.registry import register_adapter
from backend.app.llm.enums import MediaErrorCode
from backend.common.log import log


# OpenAI 错误映射
OPENAI_ERROR_MAP = {
    'content_policy_violation': MediaErrorCode.CONTENT_POLICY,
    'rate_limit_exceeded': MediaErrorCode.RATE_LIMITED,
    'invalid_request_error': MediaErrorCode.INVALID_PARAMS,
}


@register_adapter('openai', 'image')
class OpenAIImageAdapter(MediaAdapter):
    """DALL-E 3 图像生成（同步返回）"""

    provider_type = 'openai'
    media_type = 'image'

    def normalize_params(self, request: MediaRequest) -> dict:
        return {
            'prompt': request.prompt,
            'model': request.model,
            'n': request.n,
            'size': request.size,
            'quality': request.quality or 'standard',
            'response_format': 'url',
        }

    async def submit(self, request: MediaRequest) -> SubmitResult:
        """同步调用 OpenAI Images API"""
        params = self.normalize_params(request)
        url = f'{self.api_base_url or "https://api.openai.com/v1"}/images/generations'

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                resp = await client.post(
                    url,
                    json=params,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json',
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                urls = [item['url'] for item in data.get('data', [])]
                revised_prompt = data['data'][0].get('revised_prompt') if data.get('data') else None

                log.info(f'[OpenAI Image] 生成成功: {len(urls)} 张图片')
                return SubmitResult(
                    vendor_urls=urls,
                    is_async=False,
                    revised_prompt=revised_prompt,
                )
            except httpx.HTTPStatusError as e:
                error_body = e.response.json() if e.response.content else {}
                error_info = error_body.get('error', {})
                error_code = error_info.get('code', '')
                error_message = error_info.get('message', str(e))
                mapped_code = OPENAI_ERROR_MAP.get(error_code, MediaErrorCode.VENDOR_ERROR)
                log.error(f'[OpenAI Image] API 错误: {error_code} - {error_message}')
                raise OpenAIImageError(mapped_code, error_message) from e

    async def poll(self, vendor_task_id: str) -> PollResult:
        """DALL-E 3 是同步的，不需要轮询"""
        return PollResult(status='completed', progress=100)


class OpenAIImageError(Exception):
    """OpenAI 图像生成错误"""

    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(message)
