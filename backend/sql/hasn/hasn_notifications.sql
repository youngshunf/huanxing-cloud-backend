-- =====================================================
-- HASN 通知队列表
-- =====================================================
CREATE TABLE "public"."hasn_notifications" (
  "id"           bigserial PRIMARY KEY,
  "target_id"    varchar(36) NOT NULL,
  "type"         varchar(30) NOT NULL,
  "title"        varchar(200) NOT NULL,
  "body"         text,
  "data"         jsonb NOT NULL DEFAULT '{}',
  "read"         boolean NOT NULL DEFAULT false,
  "created_time" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time" timestamptz(6)
);

CREATE INDEX "idx_notif_target" ON "public"."hasn_notifications" ("target_id", "read", "created_time");
CREATE INDEX "idx_notif_type" ON "public"."hasn_notifications" ("type");

COMMENT ON TABLE "public"."hasn_notifications" IS 'HASN 通知队列表';
COMMENT ON COLUMN "public"."hasn_notifications"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_notifications"."target_id" IS '通知目标 hasn_id';
COMMENT ON COLUMN "public"."hasn_notifications"."type" IS '通知类型 (contact_request:好友请求:blue/contact_accepted:好友接受:green/message_summary:消息摘要:cyan/event_reminder:事件提醒:orange/system:系统通知:gray)';
COMMENT ON COLUMN "public"."hasn_notifications"."title" IS '通知标题';
COMMENT ON COLUMN "public"."hasn_notifications"."body" IS '通知正文';
COMMENT ON COLUMN "public"."hasn_notifications"."data" IS '附加数据 (JSONB)';
COMMENT ON COLUMN "public"."hasn_notifications"."read" IS '是否已读';
COMMENT ON COLUMN "public"."hasn_notifications"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_notifications"."updated_time" IS '更新时间';
