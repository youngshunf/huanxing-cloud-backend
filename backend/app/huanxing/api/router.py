from fastapi import APIRouter

from backend.app.huanxing.api.v1.huanxing_server import router as huanxing_server_router
from backend.app.huanxing.api.v1.huanxing_user import router as huanxing_user_router
from backend.app.huanxing.api.v1.huanxing_document import router as huanxing_document_router
from backend.app.huanxing.api.v1.huanxing_document_version import router as huanxing_document_version_router
from backend.app.huanxing.api.v1.huanxing_document_autosave import router as huanxing_document_autosave_router
from backend.app.huanxing.api.v1.huanxing_dashboard import router as huanxing_dashboard_router
from backend.core.conf import settings

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/huanxing', tags=['唤星服务'])

v1.include_router(huanxing_document_autosave_router, prefix='/document/autosaves', tags=['唤星文档-自动保存'])
v1.include_router(huanxing_document_version_router, prefix='/document/versions', tags=['唤星文档-版本'])
v1.include_router(huanxing_document_router, prefix='/documents', tags=['唤星文档'])
v1.include_router(huanxing_user_router, prefix='/users', tags=['唤星用户'])
v1.include_router(huanxing_server_router, prefix='/servers', tags=['唤星服务器'])
v1.include_router(huanxing_dashboard_router, prefix='/dashboard', tags=['唤星数据看板'])
