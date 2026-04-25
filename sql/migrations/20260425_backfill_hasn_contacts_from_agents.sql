-- 20260425 · 回填 hasn_contacts：从 hasn_agents 反向插入 owner→agent 关系
--
-- 背景：US-001 让 register_hasn_agent 注册时自动写 hasn_contacts，
-- 但存量 agent（US-001 之前创建的）从未补过 contacts。
-- 结果 hasn-node 拉服务端 contacts → 本地 contacts 表为空 →
-- chat_sessions.title 永远 NULL → 桌面端 fallback 显示原始 a_<uuid>。
--
-- 本脚本一次性回填：每个 hasn_agents 行生成一条 owner→agent 的
-- relation_type='service' / trust_level=5 / status='connected' 记录；
-- ON CONFLICT 幂等。
--
-- nickname 取 hasn_agents.name（如"星源"），与桌面端 display_name 对齐。

INSERT INTO hasn_contacts (
    owner_id,
    peer_id,
    peer_owner_id,
    peer_type,
    relation_type,
    trust_level,
    status,
    nickname,
    created_time,
    updated_time
)
SELECT
    a.owner_id,
    a.hasn_id AS peer_id,
    a.owner_id AS peer_owner_id,   -- 自家 agent：peer_owner = owner
    'agent' AS peer_type,
    'service' AS relation_type,
    5 AS trust_level,               -- owner 对自家 agent 最高信任
    'connected' AS status,
    a.name AS nickname,             -- 把 agent display name 作为联系人昵称
    a.created_time,
    NOW()
FROM hasn_agents a
WHERE a.status = 'active'
  AND NOT EXISTS (
      SELECT 1 FROM hasn_contacts c
      WHERE c.owner_id = a.owner_id
        AND c.peer_id = a.hasn_id
        AND c.relation_type = 'service'
  )
ON CONFLICT (owner_id, peer_id, relation_type) DO NOTHING;
