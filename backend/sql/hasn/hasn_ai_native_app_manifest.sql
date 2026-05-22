CREATE TABLE IF NOT EXISTS hasn_ai_native_app_manifest (
    id BIGSERIAL PRIMARY KEY,
    app_id VARCHAR(64) NOT NULL,
    version VARCHAR(40) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'draft',
    workspace_scope JSONB NOT NULL DEFAULT '[]'::jsonb,
    collaboration_mode VARCHAR(24) NOT NULL DEFAULT 'none',
    manifest_json JSONB NOT NULL,
    manifest_hash VARCHAR(128) NOT NULL,
    created_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_time TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    UNIQUE (app_id, version)
);

CREATE INDEX IF NOT EXISTS idx_ai_native_manifest_app_status
    ON hasn_ai_native_app_manifest (app_id, status);
