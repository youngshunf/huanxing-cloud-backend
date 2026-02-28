from typing import Annotated

from fastapi import APIRouter, Path, Query

from backend.app.huanxing.service.huanxing_document_service import huanxing_document_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '/share/{share_token}',
    summary='访问分享文档（公开接口，无需登录）',
)
async def get_shared_document(
    db: CurrentSession,
    share_token: Annotated[str, Path(description='分享token')],
    password: Annotated[str | None, Query(description='密码(如需要)')] = None,
) -> ResponseModel:
    document = await huanxing_document_service.get_shared_document(
        db=db,
        share_token=share_token,
        password=password,
    )
    return response_base.success(data=document)
