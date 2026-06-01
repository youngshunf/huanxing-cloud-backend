CREATE TABLE hasn_agent_mcp_keys (
    id              BIGSERIAL PRIMARY KEY,
    agent_hasn_id   VARCHAR(64) NOT NULL,
    owner_hasn_id   VARCHAR(64) NOT NULL,
    owner_user_id   BIGINT REFERENCES sys_user(id),
    key_prefix      VARCHAR(32) NOT NULL,
    key_hash        VARCHAR(64) NOT NULL,
    scopes          JSONB NOT NULL DEFAULT '[]',
    node_id         VARCHAR(128),
    status          VARCHAR(16) NOT NULL DEFAULT 'active',
    expire_time     TIMESTAMPTZ,
    last_used_time  TIMESTAMPTZ,
    created_time    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_time    TIMESTAMPTZ
);

CREATE UNIQUE INDEX uq_hasn_agent_mcp_keys_key_hash ON hasn_agent_mcp_keys(key_hash);
CREATE INDEX ix_hasn_agent_mcp_keys_agent ON hasn_agent_mcp_keys(agent_hasn_id);
CREATE INDEX ix_hasn_agent_mcp_keys_owner ON hasn_agent_mcp_keys(owner_hasn_id);

COMMENT ON TABLE hasn_agent_mcp_keys IS 'Agent MCP 接入凭证（稳定可吊销 API Key，落库只存哈希）';
COMMENT ON COLUMN hasn_agent_mcp_keys.agent_hasn_id IS '归属 Agent 的 HASN ID';
COMMENT ON COLUMN hasn_agent_mcp_keys.owner_hasn_id IS '主人 HASN ID';
COMMENT ON COLUMN hasn_agent_mcp_keys.owner_user_id IS '主人 sys_user.id';
COMMENT ON COLUMN hasn_agent_mcp_keys.key_prefix IS '明文前缀（展示/审计用，不可反推完整 key）';
COMMENT ON COLUMN hasn_agent_mcp_keys.key_hash IS 'SHA-256(完整 key) 十六进制，查表入口，唯一索引';
COMMENT ON COLUMN hasn_agent_mcp_keys.scopes IS 'scope 集（与 Agent JWT 同语义的字符串数组）';
COMMENT ON COLUMN hasn_agent_mcp_keys.node_id IS '设备绑定 node_id（空=不限设备；默认签发即绑当前 node）';
COMMENT ON COLUMN hasn_agent_mcp_keys.status IS '状态 (active:启用:green/revoked:已吊销:red)';
COMMENT ON COLUMN hasn_agent_mcp_keys.expire_time IS '过期时间（空=不过期，生命周期靠吊销/轮换管理）';
COMMENT ON COLUMN hasn_agent_mcp_keys.last_used_time IS '最近使用时间（审计 / 可疑使用排查）';
