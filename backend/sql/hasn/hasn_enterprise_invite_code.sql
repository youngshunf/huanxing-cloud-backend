CREATE TABLE hasn_enterprise_invite_code (
    id            BIGSERIAL PRIMARY KEY,
    enterprise_id BIGINT NOT NULL REFERENCES hasn_enterprise(id) ON DELETE CASCADE,
    code          VARCHAR(32) NOT NULL UNIQUE,
    created_by    BIGINT NOT NULL REFERENCES sys_user(id),
    max_uses      INT,
    used_count    INT NOT NULL DEFAULT 0,
    expires_at    TIMESTAMPTZ,
    auto_approve  BOOLEAN NOT NULL DEFAULT FALSE,
    revoked       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_hasn_enterprise_invite_code_enterprise
    ON hasn_enterprise_invite_code(enterprise_id, revoked);

COMMENT ON TABLE hasn_enterprise_invite_code IS '企业邀请码 (max_uses 为空表示无限制；auto_approve=true 时凭码加入直接通过)';
