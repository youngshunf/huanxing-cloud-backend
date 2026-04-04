-- HASN 统一实体架构 v5.0 — DB 迁移
-- 适用于: hasn_agents 和 hasn_clients 表
-- 执行时间: 2026-04-04

-- 1. hasn_clients: 添加 Node Key 哈希列（核心变更）
ALTER TABLE hasn_clients ADD COLUMN IF NOT EXISTS api_key_hash VARCHAR(64) DEFAULT NULL;
COMMENT ON COLUMN hasn_clients.api_key_hash IS 'Node Key (hasn_nk_) 的 SHA256 哈希';

-- 2. hasn_clients: 添加承载量列
ALTER TABLE hasn_clients ADD COLUMN IF NOT EXISTS capacity INTEGER DEFAULT 1;
COMMENT ON COLUMN hasn_clients.capacity IS '最大 Agent 承载量（桌面端默认1，云端可配置）';

-- 3. hasn_clients: 允许 user_hasn_id 为 NULL（节点不再绑定用户）
ALTER TABLE hasn_clients ALTER COLUMN user_hasn_id DROP NOT NULL;
ALTER TABLE hasn_clients ALTER COLUMN user_hasn_id SET DEFAULT NULL;

-- 4. hasn_clients: 更新列注释
COMMENT ON COLUMN hasn_clients.user_hasn_id IS '初始注册用户（仅用于审计记录，不再用于路由）';

-- 5. hasn_agents: 新增 capabilities 列
ALTER TABLE hasn_agents ADD COLUMN IF NOT EXISTS capabilities JSONB DEFAULT NULL;
COMMENT ON COLUMN hasn_agents.capabilities IS 'Agent 能力列表（A2A AgentCard 兼容 JSONB）';

-- 6. hasn_agents: 更新 role 默认值
ALTER TABLE hasn_agents ALTER COLUMN role SET DEFAULT 'specialist';

-- 7. hasn_agents: 标记废弃列（不删除，保持兼容）
COMMENT ON COLUMN hasn_agents.server_id IS '[废弃] 云端 Agent 所在服务器 ID — v5.0 后不再使用';
COMMENT ON COLUMN hasn_agents.home_client_id IS '[废弃] 本地 Agent 归属客户端 ID — v5.0 后被统一节点模型取代';
