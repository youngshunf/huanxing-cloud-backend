"""图像生成 API"""

from typing import Annotated

from fastapi import APIRouter, Header, Request

from backend.app.llm.schema.image import ImageGenerationRequest, ImageGenerationResponse
from backend.app.llm.service.media_service import media_service
from backend.common.log import log
from backend.database.db import CurrentSession

router = APIRouter()


def _get_client_ip(request: Request) -> str | None:
    """获取客户端 IP"""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else None


@router.post(
    '/generations',
    summary='图像生成',
    description='OpenAI 兼容图像生成接口，使用 x-api-key 认证',
    response_model=ImageGenerationResponse,
    response_model_exclude_none=True,
)
async def generate_image(
    request: Request,
    db: CurrentSession,
    body: ImageGenerationRequest,
    x_api_key: Annotated[str, Header(alias='x-api-key', description='LLM API Key (sk-cf-xxx)')],
) -> ImageGenerationResponse:
    log.info(f'[Image API] 收到图像生成请求: model={body.model}, n={body.n}, size={body.size}')
    ip_address = _get_client_ip(request)

    return await media_service.generate_image(
        db,
        api_key=x_api_key,
        request=body,
        ip_address=ip_address,
    )


@router.get(
    '/generations/{task_id}',
    summary='查询图像任务',
    description='查询图像生成任务状态',
    response_model=ImageGenerationResponse,
    response_model_exclude_none=True,
)
async def get_image_task(
    db: CurrentSession,
    task_id: str,
) -> ImageGenerationResponse:
    return await media_service.get_image_task(db, task_id)
