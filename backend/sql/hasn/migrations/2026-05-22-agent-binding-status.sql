-- Agent binding 状态字段
-- 用于记录 agent 绑定在哪个 node，以及 binding 状态

ALTER TABLE hasn_agents
ADD COLUMN binding_node_id VARCHAR(64) DEFAULT NULL,
ADD COLUMN binding_status VARCHAR(32) DEFAULT 'unbound',
ADD COLUMN binding_updated_at BIGINT DEFAULT NULL;

COMMENT ON COLUMN hasn_agents.binding_node_id IS 'Agent 当前绑定的 node ID';
COMMENT ON COLUMN hasn_agents.binding_status IS 'binding 状态: unbound/binding/bound/failed';
COMMENT ON COLUMN hasn_agents.binding_updated_at IS 'binding 状态更新时间（Unix 秒）';

-- 为 binding_node_id 创建索引，方便查询某个 node 上绑定的所有 agent
CREATE INDEX idx_hasn_agents_binding_node ON hasn_agents(binding_node_id);

-- 为 binding_status 创建索引，方便查询特定状态的 agent
CREATE INDEX idx_hasn_agents_binding_status ON hasn_agents(binding_status);
