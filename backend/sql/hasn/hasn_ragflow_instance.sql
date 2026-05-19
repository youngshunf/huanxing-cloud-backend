CREATE TABLE hasn_ragflow_instance (
    id                      BIGSERIAL PRIMARY KEY,
    scope                   VARCHAR(16) NOT NULL,
    enterprise_id           BIGINT REFERENCES hasn_enterprise(id),
    url                     VARCHAR(512) NOT NULL,
    admin_api_key_encrypted BYTEA NOT NULL,
    public_pem              TEXT NOT NULL,
    default_embd_id         VARCHAR(128),
    default_llm_id          VARCHAR(128),
    status                  VARCHAR(16) NOT NULL DEFAULT 'pending_config',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(enterprise_id),
    CHECK ((scope = 'public' AND enterprise_id IS NULL)
        OR (scope = 'enterprise' AND enterprise_id IS NOT NULL))
);

CREATE INDEX idx_hasn_ragflow_instance_status ON hasn_ragflow_instance(status);

COMMENT ON TABLE hasn_ragflow_instance IS 'RAGFlow 实例配置 (scope: public:公共:blue/enterprise:企业:purple)';
COMMENT ON COLUMN hasn_ragflow_instance.scope IS '作用域 (public:公共:blue/enterprise:企业:purple)';
COMMENT ON COLUMN hasn_ragflow_instance.status IS '状态 (pending_config:待配置:orange/active:可用:green/disabled:停用:gray)';
