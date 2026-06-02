-- 迁移 拆分 hasn_contact_requests 请求表
-- 依据 decisions/engineering/2026-05-30-contact-requests-table-split.md 第五节
-- 把 hasn_contacts 里的 pending 行搬到独立的请求表 hasn_contact_requests，然后从 hasn_contacts 删除
-- archived 行不动（无法区分拒绝与软删好友，且新代码只认 connected，archived 自然失活）
-- 原子 + 幂等：BEGIN/COMMIT 包住，ON CONFLICT DO NOTHING 防重跑插重复 pending（部分唯一索引）
-- 前置：hasn_contact_requests 表须已由 fba codegen 建好（backend/sql/hasn/hasn_contact_requests.sql）

BEGIN;

INSERT INTO "public"."hasn_contact_requests" (
    from_id, from_type, to_id, to_type, to_owner_id,
    relation_type, requested_trust_level, message, status, channel_source, created_time
)
SELECT
    owner_id,
    'human',
    peer_id,
    peer_type,
    COALESCE(peer_owner_id, peer_id),
    relation_type,
    2,
    request_message,
    'pending',
    channel_source,
    created_time
FROM "public"."hasn_contacts"
WHERE status = 'pending'
ON CONFLICT (from_id, to_id, relation_type) WHERE status = 'pending' DO NOTHING;

DELETE FROM "public"."hasn_contacts" WHERE status = 'pending';

COMMIT;
