-- 通知表对齐社区用法（doc-13 §2.1.5）
-- 1) target_id 对齐 hasn_id 宽度（修复 varchar(36) 可能截断 h_{uuid}/a_{uuid}）
ALTER TABLE "public"."hasn_notifications"
  ALTER COLUMN "target_id" TYPE varchar(40);

-- 2) 扩展 type 字典注释（值集在应用层枚举，DB 注释同步）
COMMENT ON COLUMN "public"."hasn_notifications"."type" IS
  '通知类型 (contact_request:好友请求:blue/contact_accepted:好友接受:green/message_summary:消息摘要:cyan/event_reminder:事件提醒:orange/system:系统通知:gray/community_like:社区点赞:pink/community_comment:社区评论:blue/community_follow:社区关注:green/community_collect:社区收藏:orange/community_draft_pending:草稿待确认:purple/community_mention:被提及:cyan)';

-- 3) actor 查询索引（按触发者过滤"只看 Agent 相关"等）
CREATE INDEX IF NOT EXISTS "idx_notif_actor"
  ON "public"."hasn_notifications" ((data->'actor'->>'hasn_id'));
