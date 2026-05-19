CREATE TABLE hasn_workspace_app (
    id              BIGSERIAL PRIMARY KEY,
    workspace_kind  VARCHAR(16) NOT NULL,
    user_id         BIGINT REFERENCES sys_user(id),
    enterprise_id   BIGINT REFERENCES hasn_enterprise(id),
    app_id          VARCHAR(64) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'active',
    config          JSONB NOT NULL DEFAULT '{}',
    enabled_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    enabled_by      BIGINT REFERENCES sys_user(id),
    CHECK ((workspace_kind = 'personal' AND user_id IS NOT NULL AND enterprise_id IS NULL)
        OR (workspace_kind = 'enterprise' AND enterprise_id IS NOT NULL AND user_id IS NULL))
);

CREATE UNIQUE INDEX uq_hasn_workspace_app_personal
    ON hasn_workspace_app(user_id, app_id) WHERE workspace_kind = 'personal';
CREATE UNIQUE INDEX uq_hasn_workspace_app_enterprise
    ON hasn_workspace_app(enterprise_id, app_id) WHERE workspace_kind = 'enterprise';

COMMENT ON TABLE hasn_workspace_app IS '工作空间挂载的应用 (workspace_kind: personal:个人:gray/enterprise:企业:purple)';
COMMENT ON COLUMN hasn_workspace_app.status IS '状态 (active:启用:green/disabled:停用:gray)';
