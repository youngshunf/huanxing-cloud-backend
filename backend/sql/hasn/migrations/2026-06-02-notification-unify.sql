-- =====================================================
-- 统一通知服务 P1：hasn_notifications 超集迁移（additive，零破坏）
-- 设计事实源：docs/hasn-node设计文档/通知系统统一设计/00-统一通知服务设计.md §4.1
-- 仅加列 + 回填 + 加索引，旧 app/hasn 与社区 service 读写不受影响。
-- =====================================================

ALTER TABLE "public"."hasn_notifications"
  ADD COLUMN IF NOT EXISTS "category"   varchar(20)  NOT NULL DEFAULT 'system',
  ADD COLUMN IF NOT EXISTS "priority"   varchar(10)  NOT NULL DEFAULT 'normal',
  ADD COLUMN IF NOT EXISTS "source"     jsonb        NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS "dedupe_key" varchar(120),
  ADD COLUMN IF NOT EXISTS "group_key"  varchar(120),
  ADD COLUMN IF NOT EXISTS "delivery"   jsonb        NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS "state"      varchar(12)  NOT NULL DEFAULT 'unread';

COMMENT ON COLUMN "public"."hasn_notifications"."category"   IS '通知粗类 (social:社交:blue/contact:联系人:cyan/message:消息:geekblue/agent:分身:purple/app:应用:orange/commerce:交易:gold/system:系统:gray/reminder:提醒:volcano)';
COMMENT ON COLUMN "public"."hasn_notifications"."priority"   IS '优先级 (critical/high/normal/low)，对齐协议 metadata.priority';
COMMENT ON COLUMN "public"."hasn_notifications"."source"     IS '发送主体 NotificationSource {kind,id,display_name,avatar,on_behalf_of}';
COMMENT ON COLUMN "public"."hasn_notifications"."dedupe_key" IS '去重键（同 target_id+dedupe_key 近窗未读折叠）';
COMMENT ON COLUMN "public"."hasn_notifications"."group_key"  IS '聚合键，默认 {type}:{target.id}';
COMMENT ON COLUMN "public"."hasn_notifications"."delivery"   IS '投递策略落地结果 {channels,dnd_suppressed,card_message_id}';
COMMENT ON COLUMN "public"."hasn_notifications"."state"      IS '状态 (unread:未读/read:已读/archived:归档)';

-- 回填：category 由 type 推导（D5 审批项特例须先于 community_% 规则）
UPDATE "public"."hasn_notifications" SET category = CASE
  WHEN type = 'community_draft_pending' THEN 'agent'
  WHEN type LIKE 'community_%'          THEN 'social'
  WHEN type IN ('contact_request','contact_accepted') THEN 'contact'
  WHEN type = 'message_summary'         THEN 'message'
  WHEN type = 'event_reminder'          THEN 'reminder'
  ELSE 'system' END
WHERE category = 'system';

-- 回填：state 由 read 推导
UPDATE "public"."hasn_notifications" SET state = CASE WHEN read THEN 'read' ELSE 'unread' END;

-- 回填：group_key 默认 {type}:{target.id}（data.target.id 缺失则退化为 {type}:）
UPDATE "public"."hasn_notifications"
SET group_key = type || ':' || COALESCE(data #>> '{target,id}', '')
WHERE group_key IS NULL;

CREATE INDEX IF NOT EXISTS "idx_notif_category" ON "public"."hasn_notifications" ("target_id","category","state","created_time");
CREATE INDEX IF NOT EXISTS "idx_notif_dedupe"   ON "public"."hasn_notifications" ("target_id","dedupe_key");
CREATE INDEX IF NOT EXISTS "idx_notif_source"   ON "public"."hasn_notifications" ((source->>'kind'),(source->>'id'));
