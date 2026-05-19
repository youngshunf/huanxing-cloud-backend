CREATE TABLE hasn_user_active_workspace (
    user_id       BIGINT PRIMARY KEY REFERENCES sys_user(id),
    kind          VARCHAR(16) NOT NULL DEFAULT 'personal',
    enterprise_id BIGINT REFERENCES hasn_enterprise(id),
    switched_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK ((kind = 'personal' AND enterprise_id IS NULL)
        OR (kind = 'enterprise' AND enterprise_id IS NOT NULL))
);

COMMENT ON TABLE hasn_user_active_workspace IS '每账号当前活跃的工作区，决定 daemon 拉取哪份资源 (kind: personal:个人:gray/enterprise:企业:purple)';
COMMENT ON COLUMN hasn_user_active_workspace.kind IS '类型 (personal:个人:gray/enterprise:企业:purple)';
