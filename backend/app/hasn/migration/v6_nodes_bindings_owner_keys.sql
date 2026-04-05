-- v6: 从 hasn_clients 迁移到 hasn_nodes / hasn_owner_api_keys
-- 说明:
-- 1. 本脚本做“可重复执行”的数据回填，不删除旧表
-- 2. 旧的 hasn_clients 中混存了两类数据:
--    - 真实 Node 记录
--    - 早期误存到客户端表中的 Owner API Key 记录（通常 generated_by=user_ui 或 client_type=api_key）
-- 3. 现阶段先迁移数据并保留兼容层，后续再移除旧表引用

BEGIN;

-- 1) 将旧 hasn_clients 中的真实节点回填到 hasn_nodes
INSERT INTO public.hasn_nodes (
    node_id,
    node_type,
    node_name,
    node_info,
    node_key_hash,
    capacity,
    created_by_owner_id,
    last_seen_at,
    status,
    created_time,
    updated_time
)
SELECT
    hc.client_id AS node_id,
    hc.client_type AS node_type,
    hc.device_name AS node_name,
    COALESCE(hc.device_info, '{}'::jsonb) AS node_info,
    hc.api_key_hash AS node_key_hash,
    COALESCE(hc.capacity, 1) AS capacity,
    hc.user_hasn_id AS created_by_owner_id,
    hc.last_seen_at,
    hc.status,
    hc.created_time,
    hc.updated_time
FROM public.hasn_clients hc
WHERE (
    hc.client_type IS DISTINCT FROM 'api_key'
    AND COALESCE(hc.device_info ->> 'generated_by', '') <> 'user_ui'
)
AND NOT EXISTS (
    SELECT 1 FROM public.hasn_nodes hn WHERE hn.node_id = hc.client_id
);

-- 2) 将旧 hasn_clients 中误存在客户端表里的 Owner API Key 回填到 hasn_owner_api_keys
INSERT INTO public.hasn_owner_api_keys (
    key_id,
    owner_id,
    key_name,
    key_hash,
    status,
    scopes,
    bound_node_id,
    expires_at,
    last_used_at,
    revoked_at,
    revoke_reason,
    created_time,
    updated_time
)
SELECT
    hc.client_id AS key_id,
    hc.user_hasn_id AS owner_id,
    COALESCE(hc.device_name, 'Migrated Owner Key') AS key_name,
    hc.api_key_hash AS key_hash,
    CASE
        WHEN hc.status = 'disabled' THEN 'revoked'
        WHEN hc.status = 'deleted' THEN 'deleted'
        ELSE 'active'
    END AS status,
    '{"bind_owner": true, "register_agent": true}'::jsonb AS scopes,
    NULL AS bound_node_id,
    NULL AS expires_at,
    hc.last_seen_at AS last_used_at,
    NULL AS revoked_at,
    CASE
        WHEN hc.status = 'disabled' THEN 'migrated_disabled'
        WHEN hc.status = 'deleted' THEN 'migrated_deleted'
        ELSE NULL
    END AS revoke_reason,
    hc.created_time,
    hc.updated_time
FROM public.hasn_clients hc
WHERE (
    hc.client_type = 'api_key'
    OR COALESCE(hc.device_info ->> 'generated_by', '') = 'user_ui'
)
AND hc.api_key_hash IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM public.hasn_owner_api_keys hok WHERE hok.key_id = hc.client_id
);

COMMIT;
