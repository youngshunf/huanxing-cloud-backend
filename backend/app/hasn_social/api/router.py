from fastapi import APIRouter
from backend.core.conf import settings

# 业务接口
from backend.app.hasn_social.api.v1.contacts import router as contacts_router

# 管理端 CRUD 接口
from backend.app.hasn_social.api.v1.admin.hasn_contacts import router as admin_contacts_router

# 业务路由
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/social')
v1.include_router(contacts_router)

# 管理端路由
v1.include_router(admin_contacts_router, prefix='/admin/contacts', tags=['HASN联系人管理'])
