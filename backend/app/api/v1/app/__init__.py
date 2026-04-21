"""M1 移动端 App 聚合路由.

挂载位置: /api/v1/app
"""
from fastapi import APIRouter

from backend.app.api.v1.app.owner_api_keys import router as owner_api_keys_router
from backend.app.api.v1.app.push_receipts import router as push_receipts_router
from backend.app.api.v1.app.push_tokens import router as push_tokens_router
from backend.core.conf import settings

app_router = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/app', tags=['移动端 App'])
app_router.include_router(owner_api_keys_router, prefix='/owner_api_keys')
app_router.include_router(push_tokens_router, prefix='/push_tokens')
app_router.include_router(push_receipts_router, prefix='/push_receipts')
