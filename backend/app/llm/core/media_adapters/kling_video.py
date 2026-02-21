"""可灵视频生成适配器"""

import time

import httpx
import jwt

from backend.app.llm.core.media_adapters.base import MediaAdapter, MediaRequest, PollResult, SubmitResult
from backend.app.llm.core.media_adapters.registry import register_adapter
from backend.app.llm.enums import MediaErrorCode
from backend.common.log import log

# 可灵 API 地址
KLING_API_BASE = 'https://api.klingai.com'

# 错误映射
KLING_ERROR_MAP = {
    'content_filter': MediaErrorCode.CONTENT_POLICY,
    'rate_limit': MediaErrorCode.RATE_LIMITED,
    'invalid_parameter': MediaErrorCode.INVALID_PARAMS,
    'insufficient_quota': MediaErrorCode.QUOTA_EXCEEDED,
}


def _generate_kling_token(access_key: str, secret_key: str) -> str:
    """生成可灵 API JWT Token"""
    now = int(time.time())
    payload = {
        'iss': access_key,
        'exp': now + 1800,  # 30 分钟有效
        'nbf': now - 5,
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


@register_adapter('kling', 'video')
class KlingVideoAdapter(MediaAdapter):
    """可灵视频生成（异步轮询）"""

    provider_type = 'kling'
    media_type = 'video'

    def _get_auth_header(self) -> dict:
        """获取认证头，api_key 格式: access_key:secret_key"""
        if not self.api_key or ':' not in self.api_key:
            raise KlingVideoError(MediaErrorCode.MODEL_UNAVAILABLE, '可灵 API Key 格式错误，需要 access_key:secret_key')
        access_key, secret_key = self.api_key.split(':', 1)
        token = _generate_kling_token(access_key, secret_key)
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    def normalize_params(self, request: MediaRequest) -> dict:
        params = {
            'model_name': request.model or 'kling-v1',
            'prompt': request.prompt,
            'cfg_scale': request.cfg_scale or 0.5,
            'mode': request.mode or 'std',
            'aspect_ratio': request.aspect_ratio or '16:9',
            'duration': str(request.duration or 5),
        }
        if request.image_url:
            params['image'] = request.image_url
        return params

    async def submit(self, request: MediaRequest) -> SubmitResult:
        """提交视频生成任务"""
        params = self.normalize_params(request)
        url = f'{self.api_base_url or KLING_API_BASE + "/v1"}/videos/text2video'

        if request.image_url:
            url = f'{self.api_base_url or KLING_API_BASE + "/v1"}/videos/image2video'

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(url, json=params, headers=self._get_auth_header())
                resp.raise_for_status()
                data = resp.json()

                task_data = data.get('data', {})
                task_id = task_data.get('task_id')

                if not task_id:
                    raise KlingVideoError(MediaErrorCode.VENDOR_ERROR, f'未返回 task_id: {data}')

                log.info(f'[Kling Video] 任务已提交: {task_id}')
                return SubmitResult(
                    vendor_task_id=task_id,
                    is_async=True,
                    estimated_seconds=120,
                )
            except httpx.HTTPStatusError as e:
                error_body = e.response.json() if e.response.content else {}
                error_code = error_body.get('code', '')
                error_message = error_body.get('message', str(e))
                mapped_code = KLING_ERROR_MAP.get(str(error_code), MediaErrorCode.VENDOR_ERROR)
                log.error(f'[Kling Video] 提交失败: {error_code} - {error_message}')
                raise KlingVideoError(mapped_code, error_message) from e

    async def poll(self, vendor_task_id: str) -> PollResult:
        """轮询视频生成状态"""
        url = f'{self.api_base_url or KLING_API_BASE + "/v1"}/videos/text2video/{vendor_task_id}'

        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(url, headers=self._get_auth_header())
                resp.raise_for_status()
                data = resp.json()

                task_data = data.get('data', {})
                task_status = task_data.get('task_status', '')

                if task_status == 'succeed':
                    works = task_data.get('task_result', {}).get('videos', [])
                    urls = [w['url'] for w in works if w.get('url')]
                    duration = works[0].get('duration') if works else None
                    resolution = works[0].get('resolution') if works else None
                    log.info(f'[Kling Video] 任务完成: {vendor_task_id}')
                    return PollResult(
                        status='completed',
                        progress=100,
                        vendor_urls=urls,
                        duration=duration,
                        resolution=resolution,
                    )

                if task_status == 'failed':
                    error_message = task_data.get('task_status_msg', '视频生成失败')
                    log.error(f'[Kling Video] 任务失败: {vendor_task_id} - {error_message}')
                    return PollResult(
                        status='failed',
                        error_code=MediaErrorCode.VENDOR_ERROR,
                        error_message=error_message,
                    )

                # processing
                progress = task_data.get('task_progress', 0)
                return PollResult(status='processing', progress=progress)

            except httpx.HTTPStatusError as e:
                log.error(f'[Kling Video] 轮询失败: {vendor_task_id} - {e}')
                return PollResult(
                    status='failed',
                    error_code=MediaErrorCode.VENDOR_ERROR,
                    error_message=str(e),
                )


class KlingVideoError(Exception):
    """可灵视频错误"""

    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(message)
