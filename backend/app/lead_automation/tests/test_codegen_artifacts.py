from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_codegen_generated_all_crud_model_schema_api_files() -> None:
    app_root = ROOT / 'backend/app/lead_automation'
    tables = (
        'lead_source_config',
        'lead_collection_job',
        'lead_firecrawl_request',
        'lead_raw_record',
        'lead_contact',
        'lead_contact_source',
        'lead_rejected_record',
        'lead_export_batch',
        'lead_export_item',
        'lead_audit_log',
    )

    for table in tables:
        assert (app_root / f'model/{table}.py').exists()
        assert (app_root / f'schema/{table}.py').exists()
        assert (app_root / f'crud/crud_{table}.py').exists()
        assert (app_root / f'service/{table}_service.py').exists()
        assert (app_root / f'api/v1/admin/{table}.py').exists()
        assert (app_root / f'api/v1/app/{table}.py').exists()
        assert (app_root / f'api/v1/agent/{table}.py').exists()
        assert (app_root / f'api/v1/open/{table}.py').exists()

    assert not (ROOT / 'backend/plugin/lead_automation').exists()


def test_lead_automation_sql_contains_required_indexes_and_retention_default() -> None:
    sql = (ROOT / 'backend/sql/lead_automation/001_create_lead_automation_tables.sql').read_text(encoding='utf-8')

    for table in (
        'lead_source_config',
        'lead_collection_job',
        'lead_firecrawl_request',
        'lead_raw_record',
        'lead_contact',
        'lead_contact_source',
        'lead_rejected_record',
        'lead_export_batch',
        'lead_export_item',
        'lead_audit_log',
    ):
        assert f'CREATE TABLE IF NOT EXISTS {table}' in sql
        assert f'COMMENT ON TABLE {table}' in sql
    assert 'uq_lead_contact_email' in sql
    assert 'WHERE dedupe_key_email IS NOT NULL' in sql
    assert 'uq_lead_contact_phone' in sql
    assert 'WHERE dedupe_key_phone IS NOT NULL' in sql
    assert 'uq_lead_contact_domain' in sql
    assert 'WHERE dedupe_key_domain IS NOT NULL' in sql
    assert "interval '18 months'" in sql
    assert 'idx_lead_audit_log_event_type' in sql


def test_business_layer_does_not_replace_generated_crud() -> None:
    business_source = (ROOT / 'backend/app/lead_automation/service/business_service.py').read_text(encoding='utf-8')

    assert 'CRUDPlus' not in business_source
    assert 'repository' not in business_source
    assert 'from backend.app.lead_automation.model import' in business_source


def test_business_api_and_tasks_are_registered_beside_codegen_crud() -> None:
    router_source = (ROOT / 'backend/app/lead_automation/api/router.py').read_text(encoding='utf-8')
    app_business = (ROOT / 'backend/app/lead_automation/api/v1/app/business.py').read_text(encoding='utf-8')
    admin_business = (ROOT / 'backend/app/lead_automation/api/v1/admin/business.py').read_text(encoding='utf-8')
    agent_business = (ROOT / 'backend/app/lead_automation/api/v1/agent/business.py').read_text(encoding='utf-8')
    open_business = (ROOT / 'backend/app/lead_automation/api/v1/open/business.py').read_text(encoding='utf-8')
    task_source = (ROOT / 'backend/app/lead_automation/tasks.py').read_text(encoding='utf-8')
    pipeline_source = (ROOT / 'backend/app/lead_automation/service/pipeline_service.py').read_text(encoding='utf-8')

    assert 'app_business_router' in router_source
    assert 'admin_business_router' in router_source
    assert 'open_business_router' in router_source
    assert 'agent_business_router' in router_source
    assert "FASTAPI_API_V1_PATH}/lead-automation" in router_source
    assert 'open_api.include_router(open_lead_contact_router' not in router_source
    assert 'agent.include_router(agent_lead_contact_router' not in router_source
    assert "post('/jobs'" in app_business
    assert "post('/jobs/{job_id}/run'" in app_business
    assert "get('/jobs/{job_id}'" in app_business
    assert "get('/rejected'" in app_business
    assert "post('/exports'" in app_business
    assert 'request.user.id' in app_business
    assert 'run_job(db, job_id, user_id=request.user.id)' in app_business
    assert 'user_id=obj.user_id' not in app_business
    assert 'user_id: int | None = None' not in app_business
    assert "get('/admin/audit-logs'" in admin_business
    assert "delete(\n    '/admin/contacts/by-email'" in admin_business
    assert "delete(\n    '/admin/contacts/by-phone'" in admin_business
    assert "post('/admin/archive-expired'" in admin_business
    assert "post(\n    '/admin/source-configs/blacklist'" in admin_business
    assert "post(\n    '/admin/contacts/{contact_id}/extend-retention'" in admin_business
    assert "get('/status'" in agent_business
    assert "get('/healthz'" in open_business
    assert 'def lead_automation_run_job' in task_source
    assert 'def lead_automation_archive_expired' in task_source
    assert 'lead_automation_pipeline_service' in task_source
    assert 'class LeadAutomationPipelineService' in pipeline_source
    assert 'async_db_session.begin()' in task_source


def test_business_service_covers_compliance_side_effects() -> None:
    business_source = (ROOT / 'backend/app/lead_automation/service/business_service.py').read_text(encoding='utf-8')

    assert "event_type='pii_read'" in business_source
    assert "event_type='config_change'" in business_source
    assert 'async def update_blacklist' in business_source
    assert 'async def extend_retention' in business_source
    assert 'async def dsr_delete_by_email' in business_source
    assert 'daily export limit exceeded' in business_source


def test_codegen_templates_keep_generated_output_importable() -> None:
    model_template = (ROOT / 'backend/plugin/code_generator/templates/python/model.jinja').read_text(encoding='utf-8')
    router_template = (ROOT / 'backend/plugin/code_generator/templates/python/router.jinja').read_text(encoding='utf-8')
    app_template = (ROOT / 'backend/plugin/code_generator/templates/python/api_app.jinja').read_text(encoding='utf-8')
    frontend_generator = (ROOT / 'backend/plugin/code_generator/frontend/generator.py').read_text(encoding='utf-8')
    ts_api_template = (ROOT / 'backend/plugin/code_generator/templates/typescript/api.ts.jinja').read_text(encoding='utf-8')

    assert '{% endif %}' in model_template
    assert "open_api.include_router(open_{{ table_name }}_router, prefix=" in router_template
    assert 'get_list(db=db, user_id=user_id)' not in app_template
    assert 'app.replace("_", "-")' in frontend_generator
    assert 'module.replace("_", "-")' in frontend_generator
    assert 'id: number;' in ts_api_template
    assert 'create{{ class_name }}Api(data: any)' in ts_api_template


def test_docs_record_sql_first_then_table_codegen_path() -> None:
    project_root = ROOT.parent
    docs = [
        project_root / 'docs/AI自动获客任务系统/README.md',
        project_root / 'docs/AI自动获客任务系统/02-数据模型与API设计.md',
        project_root / 'docs/AI自动获客任务系统/06-MVP开发任务拆解.md',
        project_root / 'task_plan.md',
    ]
    required_table_command = (
        'uv run fba codegen generate --table '
        'lead_source_config,lead_collection_job,lead_firecrawl_request,lead_raw_record,'
        'lead_contact,lead_contact_source,lead_rejected_record,lead_export_batch,'
        'lead_export_item,lead_audit_log --app lead_automation --execute'
    )

    for path in docs:
        text = path.read_text(encoding='utf-8')
        assert required_table_command in text
        assert '手工补齐' not in text


def test_generated_frontend_api_paths_match_registered_backend_prefixes() -> None:
    frontend_api_root = ROOT.parent / 'huanxing-cloud-frontend/apps/web-antdv-next/src/api/lead_automation'
    for path in frontend_api_root.glob('*.ts'):
        text = path.read_text(encoding='utf-8')
        assert '/api/v1/lead_automation/' not in text
        assert '/api/v1/lead-automation/' in text
        assert 'export interface Lead' in text
        assert 'export interface Lead' in text and '{\n  id: number;' in text
        assert 'Params {\n  id: number;' not in text
        assert 'CreateParams {\n  id: number;' not in text
        assert 'ListResult {\n  id: number;' not in text

    source_config_api = (frontend_api_root / 'lead_source_config.ts').read_text(encoding='utf-8')
    assert '/api/v1/lead-automation/lead-source-configs' in source_config_api
    assert '/api/v1/lead-automation/lead/source/configs' not in source_config_api
