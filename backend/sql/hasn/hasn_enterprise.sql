CREATE TABLE hasn_enterprise (
    id            BIGSERIAL PRIMARY KEY,
    name          VARCHAR(128) NOT NULL,
    slug          VARCHAR(64) NOT NULL UNIQUE,
    logo          VARCHAR(512),
    industry      VARCHAR(64),
    company_size  VARCHAR(32),
    description   TEXT,
    owner_user_id BIGINT NOT NULL REFERENCES sys_user(id),
    join_policy   VARCHAR(16) NOT NULL DEFAULT 'invite_only',
    status        VARCHAR(16) NOT NULL DEFAULT 'active',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_hasn_enterprise_owner ON hasn_enterprise(owner_user_id);
CREATE INDEX idx_hasn_enterprise_status ON hasn_enterprise(status);

COMMENT ON TABLE hasn_enterprise IS '企业实体 (status: active:正常:green/suspended:已暂停:orange/deleted:已注销:red)';
COMMENT ON COLUMN hasn_enterprise.logo IS '企业 Logo';
COMMENT ON COLUMN hasn_enterprise.industry IS '所属行业';
COMMENT ON COLUMN hasn_enterprise.company_size IS '企业规模';
COMMENT ON COLUMN hasn_enterprise.join_policy IS '加入策略 (invite_only:仅邀请码:blue/open:开放申请:green/closed:关闭:gray)';
COMMENT ON COLUMN hasn_enterprise.status IS '状态 (active:正常:green/suspended:已暂停:orange/deleted:已注销:red)';
