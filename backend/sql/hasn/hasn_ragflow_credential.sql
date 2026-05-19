CREATE TABLE hasn_ragflow_credential (
    id                BIGSERIAL PRIMARY KEY,
    user_id           BIGINT NOT NULL REFERENCES sys_user(id),
    instance_id       BIGINT NOT NULL REFERENCES hasn_ragflow_instance(id) ON DELETE CASCADE,
    ragflow_user_id   VARCHAR(64) NOT NULL,
    ragflow_tenant_id VARCHAR(64) NOT NULL,
    api_key_encrypted BYTEA NOT NULL,
    status            VARCHAR(16) NOT NULL DEFAULT 'pending',
    last_error        TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, instance_id)
);

CREATE INDEX idx_hasn_ragflow_credential_user
    ON hasn_ragflow_credential(user_id, status);

COMMENT ON TABLE hasn_ragflow_credential IS '(user, instance) 凭据映射；多企业并存：一个 user 可有多份凭据 (status: pending:待provision:gray/active:已激活:green/failed:失败:red/revoked:已撤销:default)';
COMMENT ON COLUMN hasn_ragflow_credential.status IS '状态 (pending:待provision:gray/active:已激活:green/failed:失败:red/revoked:已撤销:default)';
