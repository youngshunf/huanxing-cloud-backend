-- =====================================================
-- Agent 在线状态管理字段迁移
-- 日期: 2026-05-23
-- 说明: 添加 binding_node_id, binding_status, online_status, last_heartbeat_at
--       用于支持 agent 在线状态管理和心跳机制
-- =====================================================

-- 添加 binding_node_id：agent 当前绑定的 node ID
ALTER TABLE hasn_agents
ADD COLUMN IF NOT EXISTS binding_node_id VARCHAR(64);

-- 添加 binding_status：binding 状态
ALTER TABLE hasn_agents
ADD COLUMN IF NOT EXISTS binding_status VARCHAR(32) DEFAULT 'unbound';

-- 添加 online_status：在线状态
ALTER TABLE hasn_agents
ADD COLUMN IF NOT EXISTS online_status VARCHAR(32) DEFAULT 'offline';

-- 添加 last_heartbeat_at：最后心跳时间
ALTER TABLE hasn_agents
ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ;

-- 添加索引以优化查询
CREATE INDEX IF NOT EXISTS idx_agents_online_status ON hasn_agents(online_status);
CREATE INDEX IF NOT EXISTS idx_agents_last_heartbeat ON hasn_agents(last_heartbeat_at);
CREATE INDEX IF NOT EXISTS idx_agents_binding_node ON hasn_agents(binding_node_id) WHERE binding_node_id IS NOT NULL;

-- 添加字段注释
COMMENT ON COLUMN hasn_agents.binding_node_id IS '当前绑定的 node ID（本地设备标识）';
COMMENT ON COLUMN hasn_agents.binding_status IS 'Binding 状态 (unbound:未绑定:gray/binding:绑定中:blue/bound:已绑定:green/failed:绑定失败:red)';
COMMENT ON COLUMN hasn_agents.online_status IS '在线状态 (offline:离线:gray/online:在线:green)';
COMMENT ON COLUMN hasn_agents.last_heartbeat_at IS '最后心跳时间（用于超时检测）';
