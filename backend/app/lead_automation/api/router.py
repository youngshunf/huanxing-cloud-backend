from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.lead_automation.api.v1.admin.lead_source_config import router as admin_lead_source_config_router
from backend.app.lead_automation.api.v1.admin.lead_collection_job import router as admin_lead_collection_job_router
from backend.app.lead_automation.api.v1.admin.lead_firecrawl_request import router as admin_lead_firecrawl_request_router
from backend.app.lead_automation.api.v1.admin.lead_raw_record import router as admin_lead_raw_record_router
from backend.app.lead_automation.api.v1.admin.lead_contact import router as admin_lead_contact_router
from backend.app.lead_automation.api.v1.admin.lead_contact_source import router as admin_lead_contact_source_router
from backend.app.lead_automation.api.v1.admin.lead_rejected_record import router as admin_lead_rejected_record_router
from backend.app.lead_automation.api.v1.admin.lead_export_batch import router as admin_lead_export_batch_router
from backend.app.lead_automation.api.v1.admin.lead_export_item import router as admin_lead_export_item_router
from backend.app.lead_automation.api.v1.admin.lead_audit_log import router as admin_lead_audit_log_router
from backend.app.lead_automation.api.v1.admin.business import router as admin_business_router
# --- 用户端（仅 JWT） ---
from backend.app.lead_automation.api.v1.app.lead_source_config import router as app_lead_source_config_router
from backend.app.lead_automation.api.v1.app.lead_collection_job import router as app_lead_collection_job_router
from backend.app.lead_automation.api.v1.app.lead_firecrawl_request import router as app_lead_firecrawl_request_router
from backend.app.lead_automation.api.v1.app.lead_raw_record import router as app_lead_raw_record_router
from backend.app.lead_automation.api.v1.app.lead_contact import router as app_lead_contact_router
from backend.app.lead_automation.api.v1.app.lead_contact_source import router as app_lead_contact_source_router
from backend.app.lead_automation.api.v1.app.lead_rejected_record import router as app_lead_rejected_record_router
from backend.app.lead_automation.api.v1.app.lead_export_batch import router as app_lead_export_batch_router
from backend.app.lead_automation.api.v1.app.lead_export_item import router as app_lead_export_item_router
from backend.app.lead_automation.api.v1.app.lead_audit_log import router as app_lead_audit_log_router
from backend.app.lead_automation.api.v1.app.business import router as app_business_router
# --- Agent（Agent Key） ---
from backend.app.lead_automation.api.v1.agent.lead_source_config import router as agent_lead_source_config_router
from backend.app.lead_automation.api.v1.agent.lead_collection_job import router as agent_lead_collection_job_router
from backend.app.lead_automation.api.v1.agent.lead_firecrawl_request import router as agent_lead_firecrawl_request_router
from backend.app.lead_automation.api.v1.agent.lead_raw_record import router as agent_lead_raw_record_router
from backend.app.lead_automation.api.v1.agent.lead_contact import router as agent_lead_contact_router
from backend.app.lead_automation.api.v1.agent.lead_contact_source import router as agent_lead_contact_source_router
from backend.app.lead_automation.api.v1.agent.lead_rejected_record import router as agent_lead_rejected_record_router
from backend.app.lead_automation.api.v1.agent.lead_export_batch import router as agent_lead_export_batch_router
from backend.app.lead_automation.api.v1.agent.lead_export_item import router as agent_lead_export_item_router
from backend.app.lead_automation.api.v1.agent.lead_audit_log import router as agent_lead_audit_log_router
from backend.app.lead_automation.api.v1.agent.business import router as agent_business_router
# --- 公开（无需认证） ---
from backend.app.lead_automation.api.v1.open.lead_source_config import router as open_lead_source_config_router
from backend.app.lead_automation.api.v1.open.lead_collection_job import router as open_lead_collection_job_router
from backend.app.lead_automation.api.v1.open.lead_firecrawl_request import router as open_lead_firecrawl_request_router
from backend.app.lead_automation.api.v1.open.lead_raw_record import router as open_lead_raw_record_router
from backend.app.lead_automation.api.v1.open.lead_contact import router as open_lead_contact_router
from backend.app.lead_automation.api.v1.open.lead_contact_source import router as open_lead_contact_source_router
from backend.app.lead_automation.api.v1.open.lead_rejected_record import router as open_lead_rejected_record_router
from backend.app.lead_automation.api.v1.open.lead_export_batch import router as open_lead_export_batch_router
from backend.app.lead_automation.api.v1.open.lead_export_item import router as open_lead_export_item_router
from backend.app.lead_automation.api.v1.open.lead_audit_log import router as open_lead_audit_log_router
from backend.app.lead_automation.api.v1.open.business import router as open_business_router

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/lead-automation/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/lead-automation', tags=['AI lead automation source configuration管理'])

v1.include_router(admin_lead_source_config_router, prefix='/lead-source-configs', tags=['AI lead automation source configuration管理-AI lead automation source configuration'])
v1.include_router(admin_lead_collection_job_router, prefix='/lead/collection/jobs', tags=['AI lead automation collection job-AI lead automation collection job'])
v1.include_router(admin_lead_firecrawl_request_router, prefix='/lead/firecrawl/requests', tags=['Firecrawl request audit for AI lead automation-Firecrawl request audit for AI lead automation'])
v1.include_router(admin_lead_raw_record_router, prefix='/lead/raw/records', tags=['Raw crawled lead page record-Raw crawled lead page record'])
v1.include_router(admin_lead_contact_router, prefix='/lead/contacts', tags=['Valid deduplicated lead contact-Valid deduplicated lead contact'])
v1.include_router(admin_lead_contact_source_router, prefix='/lead/contact/sources', tags=['Lead multi-source evidence-Lead multi-source evidence'])
v1.include_router(admin_lead_rejected_record_router, prefix='/lead/rejected/records', tags=['Rejected, invalid, duplicate, or failed lead record-Rejected, invalid, duplicate, or failed lead record'])
v1.include_router(admin_lead_export_batch_router, prefix='/lead/export/batchs', tags=['Lead CSV export batch-Lead CSV export batch'])
v1.include_router(admin_lead_export_item_router, prefix='/lead/export/items', tags=['Lead CSV export item snapshot-Lead CSV export item snapshot'])
v1.include_router(admin_lead_audit_log_router, prefix='/lead/audit/logs', tags=['Lead automation PII and compliance audit log-Lead automation PII and compliance audit log'])
v1.include_router(admin_business_router, tags=['AI lead automation业务接口'])

# ========================================
# 用户端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/lead-automation/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/lead-automation/app', tags=['AI lead automation source configuration用户端'])

app.include_router(app_lead_source_config_router, prefix='/lead-source-configs', tags=['AI lead automation source configuration用户端-AI lead automation source configuration'])
app.include_router(app_lead_collection_job_router, prefix='/lead/collection/jobs', tags=['AI lead automation collection job-AI lead automation collection job'])
app.include_router(app_lead_firecrawl_request_router, prefix='/lead/firecrawl/requests', tags=['Firecrawl request audit for AI lead automation-Firecrawl request audit for AI lead automation'])
app.include_router(app_lead_raw_record_router, prefix='/lead/raw/records', tags=['Raw crawled lead page record-Raw crawled lead page record'])
app.include_router(app_lead_contact_router, prefix='/lead/contacts', tags=['Valid deduplicated lead contact-Valid deduplicated lead contact'])
app.include_router(app_lead_contact_source_router, prefix='/lead/contact/sources', tags=['Lead multi-source evidence-Lead multi-source evidence'])
app.include_router(app_lead_rejected_record_router, prefix='/lead/rejected/records', tags=['Rejected, invalid, duplicate, or failed lead record-Rejected, invalid, duplicate, or failed lead record'])
app.include_router(app_lead_export_batch_router, prefix='/lead/export/batchs', tags=['Lead CSV export batch-Lead CSV export batch'])
app.include_router(app_lead_export_item_router, prefix='/lead/export/items', tags=['Lead CSV export item snapshot-Lead CSV export item snapshot'])
app.include_router(app_lead_audit_log_router, prefix='/lead/audit/logs', tags=['Lead automation PII and compliance audit log-Lead automation PII and compliance audit log'])
app.include_router(app_business_router, tags=['AI lead automation业务接口'])

# ========================================
# 公开 API（无需认证）
# 路径前缀: /api/v1/lead-automation/open/
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/lead-automation/open', tags=['AI lead automation source configuration公开'])

open_api.include_router(open_business_router, tags=['AI lead automation公开业务接口'])

# ========================================
# Agent API
# 路径前缀: /api/v1/lead-automation/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/lead-automation/agent', tags=['AI lead automation source configurationAgent'])
agent.include_router(agent_business_router, tags=['AI lead automation Agent业务接口'])
