CREATE TABLE hasn_enterprise_membership (
    id            BIGSERIAL PRIMARY KEY,
    enterprise_id BIGINT NOT NULL REFERENCES hasn_enterprise(id) ON DELETE CASCADE,
    user_id       BIGINT NOT NULL REFERENCES sys_user(id),
    role          VARCHAR(16) NOT NULL DEFAULT 'member',
    status        VARCHAR(16) NOT NULL DEFAULT 'pending',
    apply_message TEXT,
    apply_via     VARCHAR(16),
    invite_code   VARCHAR(32),
    decided_by    BIGINT REFERENCES sys_user(id),
    decided_at    TIMESTAMPTZ,
    decision_note TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX uq_hasn_enterprise_membership_active
    ON hasn_enterprise_membership(enterprise_id, user_id)
    WHERE status IN ('pending', 'approved');
CREATE INDEX idx_hasn_enterprise_membership_enterprise
    ON hasn_enterprise_membership(enterprise_id, status);
CREATE INDEX idx_hasn_enterprise_membership_user
    ON hasn_enterprise_membership(user_id, status);

COMMENT ON TABLE hasn_enterprise_membership IS '企业成员关系与申请记录（多企业：同一 user 可同时 approved 多个 enterprise）';
COMMENT ON COLUMN hasn_enterprise_membership.role IS '角色 (owner:所有者:purple/admin:管理员:blue/member:成员:green)';
COMMENT ON COLUMN hasn_enterprise_membership.status IS '状态 (pending:待审批:orange/approved:已通过:green/rejected:已拒绝:red/left:已退出:gray/removed:已移除:gray)';
