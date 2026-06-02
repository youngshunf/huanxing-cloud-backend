-- =====================================================
-- 加宽 hasn_contact_requests 的 hasn_id 列 varchar(36) -> varchar(40)
-- 与全库 hasn_id 列宽对齐（hasn_humans.hasn_id / hasn_agents.hasn_id /
-- hasn_contacts.owner_id/peer_id 均为 varchar(40)）
--
-- 根因：HASN id = 'h_'/'a_' 前缀 + 36 字符 UUID = 38 字符，varchar(36) 溢出 2 字符
-- 现象：创建好友请求 INSERT 抛 asyncpg StringDataRightTruncationError
--       (value too long for type character varying(36))
-- 关联：decisions/engineering/2026-05-30-contact-requests-table-split.md
-- =====================================================
BEGIN;
ALTER TABLE "public"."hasn_contact_requests" ALTER COLUMN "from_id"     TYPE varchar(40);
ALTER TABLE "public"."hasn_contact_requests" ALTER COLUMN "to_id"       TYPE varchar(40);
ALTER TABLE "public"."hasn_contact_requests" ALTER COLUMN "to_owner_id" TYPE varchar(40);
ALTER TABLE "public"."hasn_contact_requests" ALTER COLUMN "decided_by"  TYPE varchar(40);
COMMIT;
