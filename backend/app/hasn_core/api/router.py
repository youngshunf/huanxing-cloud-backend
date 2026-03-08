from fastapi import APIRouter
from backend.core.conf import settings
from backend.app.hasn_core.api.v1.auth import router as auth_router
from backend.app.hasn_core.api.v1.ws_sync import router as sync_router
from backend.app.hasn_core.api.v1.identity import router as identity_router
from backend.app.hasn_core.api.v1.messages import router as messages_router
from backend.app.hasn_core.api.v1.conversations import router as conversations_router

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn')
v1.include_router(auth_router)
v1.include_router(sync_router)
v1.include_router(identity_router)
v1.include_router(messages_router)
v1.include_router(conversations_router)
