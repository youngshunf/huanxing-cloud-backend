-- HASN 统一节点架构迁移
-- 在 hasn_clients 表中增加 API Key 和容量字段

ALTER TABLE hasn_clients
    ADD COLUMN IF NOT EXISTS api_key_hash VARCHAR(64) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS capacity INTEGER DEFAULT 1;

-- API Key 哈希索引（用于节点认证）
CREATE INDEX IF NOT EXISTS idx_hasn_clients_api_key_hash
    ON hasn_clients(api_key_hash)
    WHERE api_key_hash IS NOT NULL;

COMMENT ON COLUMN hasn_clients.api_key_hash IS '节点 API Key 的 SHA256 哈希';
COMMENT ON COLUMN hasn_clients.capacity IS '最大 Agent 承载量（桌面端默认1，云端可配置）';
