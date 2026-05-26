-- =====================================================
-- 2026-05-26 HASN 联系人来源回填
-- 目标:
--   1. 为系统自动创建的 service 联系人补 channel_source=system
--   2. 为社交请求/已通过的好友联系人补 channel_source=manual
--   3. 让前端不要再靠 peer 类型猜“来源”
-- =====================================================

-- 系统自动创建的 owner→agent service 关系
UPDATE "public"."hasn_contacts"
   SET "channel_source" = 'system'
 WHERE "peer_type" = 'agent'
   AND "peer_owner_id" = "owner_id"
   AND ("channel_source" IS NULL OR "channel_source" = '');

-- 社交关系里，收到/通过的好友请求默认视为手动发起
UPDATE "public"."hasn_contacts"
   SET "channel_source" = 'manual'
 WHERE "relation_type" = 'social'
   AND (
        "status" = 'pending'
        OR "request_message" IS NOT NULL
        OR ("peer_type" = 'agent' AND "peer_owner_id" IS NOT NULL AND "peer_owner_id" <> "owner_id")
   )
   AND ("channel_source" IS NULL OR "channel_source" = '');

COMMENT ON COLUMN "public"."hasn_contacts"."channel_source"
  IS '来源渠道类型 (wechat:微信:green/feishu:飞书:blue/qq:QQ:cyan/webhook:Webhook:purple/manual:好友请求:gray/system:AI分身:orange)';
