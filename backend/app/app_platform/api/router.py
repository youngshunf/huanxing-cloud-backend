from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.app_platform.api.v1.admin.platform_scopes import router as admin_platform_scopes_router
from backend.app.app_platform.api.v1.admin.app_scopes import router as admin_app_scopes_router
from backend.app.app_platform.api.v1.admin.app_permission_grants import router as admin_app_permission_grants_router
from backend.app.app_platform.api.v1.admin.app_dynamic_permission_requests import router as admin_app_dynamic_permission_requests_router
from backend.app.app_platform.api.v1.admin.permissions import router as admin_permissions_router
from backend.app.app_platform.api.v1.admin.app_developers import router as admin_app_developers_router
from backend.app.app_platform.api.v1.admin.app_agent_bindings import router as admin_app_agent_bindings_router
from backend.app.app_platform.api.v1.admin.app_manifests import router as admin_app_manifests_router
from backend.app.app_platform.api.v1.admin.app_versions import router as admin_app_versions_router
from backend.app.app_platform.api.v1.admin.app_listings import router as admin_app_listings_router
from backend.app.app_platform.api.v1.admin.app_installations import router as admin_app_installations_router
from backend.app.app_platform.api.v1.admin.app_tools import router as admin_app_tools_router
from backend.app.app_platform.api.v1.admin.app_resources import router as admin_app_resources_router
from backend.app.app_platform.api.v1.admin.app_events import router as admin_app_events_router
from backend.app.app_platform.api.v1.admin.app_reviews import router as admin_app_reviews_router
from backend.app.app_platform.api.v1.admin.app_entitlements import router as admin_app_entitlements_router
from backend.app.app_platform.api.v1.admin.app_data_records import router as admin_app_data_records_router
from backend.app.app_platform.api.v1.admin.app_permission_audit_logs import router as admin_app_permission_audit_logs_router
# --- 用户端（仅 JWT） ---
from backend.app.app_platform.api.v1.app.platform_scopes import router as app_platform_scopes_router
from backend.app.app_platform.api.v1.app.app_scopes import router as app_app_scopes_router
from backend.app.app_platform.api.v1.app.app_permission_grants import router as app_app_permission_grants_router
from backend.app.app_platform.api.v1.app.app_dynamic_permission_requests import router as app_app_dynamic_permission_requests_router
from backend.app.app_platform.api.v1.app.app_developers import router as app_app_developers_router
from backend.app.app_platform.api.v1.app.app_agent_bindings import router as app_app_agent_bindings_router
from backend.app.app_platform.api.v1.app.app_manifests import router as app_app_manifests_router
from backend.app.app_platform.api.v1.app.app_versions import router as app_app_versions_router
from backend.app.app_platform.api.v1.app.app_listings import router as app_app_listings_router
from backend.app.app_platform.api.v1.app.app_installations import router as app_app_installations_router
from backend.app.app_platform.api.v1.app.app_tools import router as app_app_tools_router
from backend.app.app_platform.api.v1.app.app_resources import router as app_app_resources_router
from backend.app.app_platform.api.v1.app.app_events import router as app_app_events_router
from backend.app.app_platform.api.v1.app.app_reviews import router as app_app_reviews_router
from backend.app.app_platform.api.v1.app.app_entitlements import router as app_app_entitlements_router
from backend.app.app_platform.api.v1.app.app_data_records import router as app_app_data_records_router
from backend.app.app_platform.api.v1.app.app_permission_audit_logs import router as app_app_permission_audit_logs_router
# --- Agent（Agent Key） ---
from backend.app.app_platform.api.v1.agent.platform_scopes import router as agent_platform_scopes_router
from backend.app.app_platform.api.v1.agent.app_scopes import router as agent_app_scopes_router
from backend.app.app_platform.api.v1.agent.app_permission_grants import router as agent_app_permission_grants_router
from backend.app.app_platform.api.v1.agent.app_dynamic_permission_requests import router as agent_app_dynamic_permission_requests_router
from backend.app.app_platform.api.v1.agent.app_developers import router as agent_app_developers_router
from backend.app.app_platform.api.v1.agent.app_agent_bindings import router as agent_app_agent_bindings_router
from backend.app.app_platform.api.v1.agent.app_manifests import router as agent_app_manifests_router
from backend.app.app_platform.api.v1.agent.app_versions import router as agent_app_versions_router
from backend.app.app_platform.api.v1.agent.app_listings import router as agent_app_listings_router
from backend.app.app_platform.api.v1.agent.app_installations import router as agent_app_installations_router
from backend.app.app_platform.api.v1.agent.app_tools import router as agent_app_tools_router
from backend.app.app_platform.api.v1.agent.app_resources import router as agent_app_resources_router
from backend.app.app_platform.api.v1.agent.app_events import router as agent_app_events_router
from backend.app.app_platform.api.v1.agent.app_reviews import router as agent_app_reviews_router
from backend.app.app_platform.api.v1.agent.app_entitlements import router as agent_app_entitlements_router
from backend.app.app_platform.api.v1.agent.app_data_records import router as agent_app_data_records_router
from backend.app.app_platform.api.v1.agent.app_permission_audit_logs import router as agent_app_permission_audit_logs_router
# --- 公开（无需认证） ---
from backend.app.app_platform.api.v1.open.platform_scopes import router as open_platform_scopes_router
from backend.app.app_platform.api.v1.open.app_scopes import router as open_app_scopes_router
from backend.app.app_platform.api.v1.open.app_permission_grants import router as open_app_permission_grants_router
from backend.app.app_platform.api.v1.open.app_dynamic_permission_requests import router as open_app_dynamic_permission_requests_router
from backend.app.app_platform.api.v1.open.app_developers import router as open_app_developers_router
from backend.app.app_platform.api.v1.open.app_agent_bindings import router as open_app_agent_bindings_router
from backend.app.app_platform.api.v1.open.app_manifests import router as open_app_manifests_router
from backend.app.app_platform.api.v1.open.app_versions import router as open_app_versions_router
from backend.app.app_platform.api.v1.open.app_listings import router as open_app_listings_router
from backend.app.app_platform.api.v1.open.app_installations import router as open_app_installations_router
from backend.app.app_platform.api.v1.open.app_tools import router as open_app_tools_router
from backend.app.app_platform.api.v1.open.app_resources import router as open_app_resources_router
from backend.app.app_platform.api.v1.open.app_events import router as open_app_events_router
from backend.app.app_platform.api.v1.open.app_reviews import router as open_app_reviews_router
from backend.app.app_platform.api.v1.open.app_entitlements import router as open_app_entitlements_router
from backend.app.app_platform.api.v1.open.app_data_records import router as open_app_data_records_router
from backend.app.app_platform.api.v1.open.app_permission_audit_logs import router as open_app_permission_audit_logs_router

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/app_platform/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/app_platform', tags=['平台权限定义表（hasn.* namespace）管理'])

v1.include_router(admin_platform_scopes_router, prefix='/platform-scopess', tags=['平台权限定义表（hasn.* namespace）管理-平台权限定义表（hasn.* namespace）'])
v1.include_router(admin_app_scopes_router, prefix='/app/scopess', tags=['应用权限定义表（{domain}.* namespace）-应用权限定义表（{domain}.* namespace）'])
v1.include_router(admin_app_permission_grants_router, prefix='/app/permission/grantss', tags=['权限授予记录-权限授予记录'])
v1.include_router(admin_app_dynamic_permission_requests_router, prefix='/app/dynamic/permission/requestss', tags=['动态权限请求-动态权限请求'])
v1.include_router(admin_permissions_router, prefix='/permissions', tags=['权限管理'])
v1.include_router(admin_app_developers_router, prefix='/app/developerss', tags=['应用开发者-应用开发者'])
v1.include_router(admin_app_agent_bindings_router, prefix='/app/agent/bindingss', tags=['Installation 绑定的 Agent 列-Installation 绑定的 Agent 列'])
v1.include_router(admin_app_manifests_router, prefix='/app/manifestss', tags=['App 清单-App 清单'])
v1.include_router(admin_app_versions_router, prefix='/app/versionss', tags=['App 版本-App 版本'])
v1.include_router(admin_app_listings_router, prefix='/app/listingss', tags=['应用市场列表-应用市场列表'])
v1.include_router(admin_app_installations_router, prefix='/app/installationss', tags=['App 安装记录-App 安装记录'])
v1.include_router(admin_app_tools_router, prefix='/app/toolss', tags=['App Tool 定义-App Tool 定义'])
v1.include_router(admin_app_resources_router, prefix='/app/resourcess', tags=['App Resource 定义-App Resource 定义'])
v1.include_router(admin_app_events_router, prefix='/app/eventss', tags=['App Event 定义-App Event 定义'])
v1.include_router(admin_app_reviews_router, prefix='/app/reviewss', tags=['App 审核记录-App 审核记录'])
v1.include_router(admin_app_entitlements_router, prefix='/app/entitlementss', tags=['App 购买凭证-App 购买凭证'])
v1.include_router(admin_app_data_records_router, prefix='/app/data/recordss', tags=['应用数据记录表（JSONB 存储）-应用数据记录表（JSONB 存储）'])
v1.include_router(admin_app_permission_audit_logs_router, prefix='/app/permission/audit/logss', tags=['权限审计日志-权限审计日志'])

# ========================================
# 用户端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/app_platform/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/app_platform/app', tags=['平台权限定义表（hasn.* namespace）用户端'])

app.include_router(app_platform_scopes_router, prefix='/platform-scopess', tags=['平台权限定义表（hasn.* namespace）用户端-平台权限定义表（hasn.* namespace）'])
app.include_router(app_app_scopes_router, prefix='/app/scopess', tags=['应用权限定义表（{domain}.* namespace）-应用权限定义表（{domain}.* namespace）'])
app.include_router(app_app_permission_grants_router, prefix='/app/permission/grantss', tags=['权限授予记录-权限授予记录'])
app.include_router(app_app_dynamic_permission_requests_router, prefix='/app/dynamic/permission/requestss', tags=['动态权限请求-动态权限请求'])
app.include_router(app_app_developers_router, prefix='/app/developerss', tags=['应用开发者-应用开发者'])
app.include_router(app_app_agent_bindings_router, prefix='/app/agent/bindingss', tags=['Installation 绑定的 Agent 列-Installation 绑定的 Agent 列'])
app.include_router(app_app_manifests_router, prefix='/app/manifestss', tags=['App 清单-App 清单'])
app.include_router(app_app_versions_router, prefix='/app/versionss', tags=['App 版本-App 版本'])
app.include_router(app_app_listings_router, prefix='/app/listingss', tags=['应用市场列表-应用市场列表'])
app.include_router(app_app_installations_router, prefix='/app/installationss', tags=['App 安装记录-App 安装记录'])
app.include_router(app_app_tools_router, prefix='/app/toolss', tags=['App Tool 定义-App Tool 定义'])
app.include_router(app_app_resources_router, prefix='/app/resourcess', tags=['App Resource 定义-App Resource 定义'])
app.include_router(app_app_events_router, prefix='/app/eventss', tags=['App Event 定义-App Event 定义'])
app.include_router(app_app_reviews_router, prefix='/app/reviewss', tags=['App 审核记录-App 审核记录'])
app.include_router(app_app_entitlements_router, prefix='/app/entitlementss', tags=['App 购买凭证-App 购买凭证'])
app.include_router(app_app_data_records_router, prefix='/app/data/recordss', tags=['应用数据记录表（JSONB 存储）-应用数据记录表（JSONB 存储）'])
app.include_router(app_app_permission_audit_logs_router, prefix='/app/permission/audit/logss', tags=['权限审计日志-权限审计日志'])

# ========================================
# 公开 API（无需认证）
# 路径前缀: /api/v1/app_platform/open/
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/app_platform/open', tags=['平台权限定义表（hasn.* namespace）公开'])

open_api.include_router(open_platform_scopes_router, prefix='/platform-scopess', tags=['平台权限定义表（hasn.* namespace）公开-平台权限定义表（hasn.* namespace）'])
open_api.include_router(open_app_scopes_router, prefix='/app/scopess', tags=['应用权限定义表（{domain}.* namespace）-应用权限定义表（{domain}.* namespace）'])
open_api.include_router(open_app_permission_grants_router, prefix='/app/permission/grantss', tags=['权限授予记录-权限授予记录'])
open_api.include_router(open_app_dynamic_permission_requests_router, prefix='/app/dynamic/permission/requestss', tags=['动态权限请求-动态权限请求'])
open_api.include_router(open_app_developers_router, prefix='/app/developerss', tags=['应用开发者-应用开发者'])
open_api.include_router(open_app_agent_bindings_router, prefix='/app/agent/bindingss', tags=['Installation 绑定的 Agent 列-Installation 绑定的 Agent 列'])
open_api.include_router(open_app_manifests_router, prefix='/app/manifestss', tags=['App 清单-App 清单'])
open_api.include_router(open_app_versions_router, prefix='/app/versionss', tags=['App 版本-App 版本'])
open_api.include_router(open_app_listings_router, prefix='/app/listingss', tags=['应用市场列表-应用市场列表'])
open_api.include_router(open_app_installations_router, prefix='/app/installationss', tags=['App 安装记录-App 安装记录'])
open_api.include_router(open_app_tools_router, prefix='/app/toolss', tags=['App Tool 定义-App Tool 定义'])
open_api.include_router(open_app_resources_router, prefix='/app/resourcess', tags=['App Resource 定义-App Resource 定义'])
open_api.include_router(open_app_events_router, prefix='/app/eventss', tags=['App Event 定义-App Event 定义'])
open_api.include_router(open_app_reviews_router, prefix='/app/reviewss', tags=['App 审核记录-App 审核记录'])
open_api.include_router(open_app_entitlements_router, prefix='/app/entitlementss', tags=['App 购买凭证-App 购买凭证'])
open_api.include_router(open_app_data_records_router, prefix='/app/data/recordss', tags=['应用数据记录表（JSONB 存储）-应用数据记录表（JSONB 存储）'])
open_api.include_router(open_app_permission_audit_logs_router, prefix='/app/permission/audit/logss', tags=['权限审计日志-权限审计日志'])

# ========================================
# Agent API
# 路径前缀: /api/v1/app_platform/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/app_platform/agent', tags=['平台权限定义表（hasn.* namespace）Agent'])

agent.include_router(agent_platform_scopes_router, prefix='/platform-scopess', tags=['平台权限定义表（hasn.* namespace）Agent-平台权限定义表（hasn.* namespace）'])
agent.include_router(agent_app_scopes_router, prefix='/app/scopess', tags=['应用权限定义表（{domain}.* namespace）-应用权限定义表（{domain}.* namespace）'])
agent.include_router(agent_app_permission_grants_router, prefix='/app/permission/grantss', tags=['权限授予记录-权限授予记录'])
agent.include_router(agent_app_dynamic_permission_requests_router, prefix='/app/dynamic/permission/requestss', tags=['动态权限请求-动态权限请求'])
agent.include_router(agent_app_developers_router, prefix='/app/developerss', tags=['应用开发者-应用开发者'])
agent.include_router(agent_app_agent_bindings_router, prefix='/app/agent/bindingss', tags=['Installation 绑定的 Agent 列-Installation 绑定的 Agent 列'])
agent.include_router(agent_app_manifests_router, prefix='/app/manifestss', tags=['App 清单-App 清单'])
agent.include_router(agent_app_versions_router, prefix='/app/versionss', tags=['App 版本-App 版本'])
agent.include_router(agent_app_listings_router, prefix='/app/listingss', tags=['应用市场列表-应用市场列表'])
agent.include_router(agent_app_installations_router, prefix='/app/installationss', tags=['App 安装记录-App 安装记录'])
agent.include_router(agent_app_tools_router, prefix='/app/toolss', tags=['App Tool 定义-App Tool 定义'])
agent.include_router(agent_app_resources_router, prefix='/app/resourcess', tags=['App Resource 定义-App Resource 定义'])
agent.include_router(agent_app_events_router, prefix='/app/eventss', tags=['App Event 定义-App Event 定义'])
agent.include_router(agent_app_reviews_router, prefix='/app/reviewss', tags=['App 审核记录-App 审核记录'])
agent.include_router(agent_app_entitlements_router, prefix='/app/entitlementss', tags=['App 购买凭证-App 购买凭证'])
agent.include_router(agent_app_data_records_router, prefix='/app/data/recordss', tags=['应用数据记录表（JSONB 存储）-应用数据记录表（JSONB 存储）'])
agent.include_router(agent_app_permission_audit_logs_router, prefix='/app/permission/audit/logss', tags=['权限审计日志-权限审计日志'])
