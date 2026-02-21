"""视频生成 API"""

from typing import Annotated

from fastapi import APIRouter, Header, Request

from backend.app.llm.schema.video import VideoGenerationRequest, VideoGenerationResponse
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
    summary='视频生成',
    description='视频生成接口，使用 x-api-key 认证',
    response_model=VideoGenerationResponse,
    response_model_exclude_none=True,
)
async def generate_video(
    request: Request,
    db: CurrentSession,
    body: VideoGenerationRequest,
    x_api_key: Annotated[str, Header(alias='x-api-key', description='LLM API Key (sk-cf-xxx)')],
) -> VideoGenerationResponse:
    log.info(f'[Video API] 收到视频生成请求: model={body.model}, duration={body.duration}')
    ip_address = _get_client_ip(request)

    return await media_service.generate_video(
        db,
        api_key=x_api_key,
        request=body,
        ip_address=ip_address,
    )


@router.get(
    '/generations/{task_id}',
    summary='查询视频任务',
    description='查询视频生成任务状态',
    response_model=VideoGenerationResponse,
    response_model_exclude_none=True,
)
async def get_video_task(
    db: CurrentSession,
    task_id: str,
) -> VideoGenerationResponse:
    return await media_service.get_video_task(db, task_id)
