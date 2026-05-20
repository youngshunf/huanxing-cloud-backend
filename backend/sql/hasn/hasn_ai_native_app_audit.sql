CREATE TABLE IF NOT EXISTS hasn_ai_native_app_audit (
    id BIGSERIAL PRIMARY KEY,
    trace_id VARCHAR(80) NOT NULL,
    step VARCHAR(32) NOT NULL DEFAULT 'runtime',
    workspace_kind VARCHAR(16) NOT NULL,
    user_id BIGINT,
    enterprise_id BIGINT,
    app_id VARCHAR(64) NOT NULL,
    app_version VARCHAR(40),
    actor_type VARCHAR(16) NOT NULL,
    agent_hasn_id VARCHAR(80),
    owner_hasn_id VARCHAR(80),
    session_uuid VARCHAR(80),
    method VARCHAR(80) NOT NULL,
    capability_id VARCHAR(120),
    tool_id VARCHAR(120),
    event_type VARCHAR(120),
    required_scopes JSONB NOT NULL DEFAULT '[]'::jsonb,
    agent_scopes_snapshot JSONB NOT NULL DEFAULT '[]'::jsonb,
    workspace_role VARCHAR(16),
    risk_level VARCHAR(16),
    decision VARCHAR(32) NOT NULL,
    confirmation_id VARCHAR(80),
    result_ref VARCHAR(255),
    error_code VARCHAR(40),
    context JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_ai_native_audit_trace_step
    ON hasn_ai_native_app_audit (trace_id, step);

CREATE INDEX IF NOT EXISTS idx_ai_native_audit_workspace_time
    ON hasn_ai_native_app_audit (workspace_kind, enterprise_id, user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_native_audit_app_time
    ON hasn_ai_native_app_audit (app_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_native_audit_agent_time
    ON hasn_ai_native_app_audit (agent_hasn_id, created_at DESC);
