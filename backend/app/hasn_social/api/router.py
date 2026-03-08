from fastapi import APIRouter
from backend.core.conf import settings
from backend.app.hasn_social.api.v1.contacts import router as contacts_router

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn')
v1.include_router(contacts_router)
