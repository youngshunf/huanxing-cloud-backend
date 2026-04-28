-- =====================================================
-- HASN 服务端下行同步事件表（S1 codegen 输入 + S4 业务写入）
-- =====================================================
CREATE TABLE "public"."hasn_sync_events" (
  "id"             bigserial PRIMARY KEY,
  "event_id"       varchar(40) NOT NULL,
  "owner_id"       varchar(40) NOT NULL,
  "hasn_id"        varchar(40) NOT NULL,
  "event_type"     varchar(50) NOT NULL,
  "aggregate_type" varchar(40) NOT NULL,
  "aggregate_id"   varchar(80) NOT NULL,
  "conversation_id" uuid,
  "payload"        jsonb NOT NULL DEFAULT '{}',
  "revision"       bigint NOT NULL,
  "occurred_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at"     timestamptz(6),
  "created_time"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"   timestamptz(6),
  CONSTRAINT "uq_hasn_sync_events_event" UNIQUE ("event_id"),
  CONSTRAINT "uq_hasn_sync_events_owner_revision" UNIQUE ("owner_id", "revision")
);

CREATE INDEX "idx_hasn_sync_events_owner_cursor" ON "public"."hasn_sync_events" ("owner_id", "revision");
CREATE INDEX "idx_hasn_sync_events_hasn" ON "public"."hasn_sync_events" ("hasn_id", "revision");
CREATE INDEX "idx_hasn_sync_events_aggregate" ON "public"."hasn_sync_events" ("aggregate_type", "aggregate_id");
CREATE INDEX "idx_hasn_sync_events_conversation" ON "public"."hasn_sync_events" ("conversation_id") WHERE "conversation_id" IS NOT NULL;

COMMENT ON TABLE "public"."hasn_sync_events" IS 'HASN 服务端下行同步事件表';
COMMENT ON COLUMN "public"."hasn_sync_events"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_sync_events"."event_id" IS '事件唯一 ID (se_{uuid})';
COMMENT ON COLUMN "public"."hasn_sync_events"."owner_id" IS '事件所属 Owner hasn_id';
COMMENT ON COLUMN "public"."hasn_sync_events"."hasn_id" IS '事件目标主体 hasn_id（Human 或 owned Agent）';
COMMENT ON COLUMN "public"."hasn_sync_events"."event_type" IS '事件类型 (message_created:消息创建:blue/inbox_updated:Inbox更新:green/profile_updated:Profile更新:orange/runtime_warning:Runtime警告:purple/channel_bound:渠道绑定:cyan)';
COMMENT ON COLUMN "public"."hasn_sync_events"."aggregate_type" IS '聚合类型 (message:消息:blue/conversation:会话:green/profile:Profile:orange/runtime:Runtime:purple/channel:渠道:cyan/sandbox:沙箱:gray)';
COMMENT ON COLUMN "public"."hasn_sync_events"."aggregate_id" IS '聚合 ID';
COMMENT ON COLUMN "public"."hasn_sync_events"."conversation_id" IS '关联会话 ID（如有）';
COMMENT ON COLUMN "public"."hasn_sync_events"."payload" IS '事件载荷（服务端权威摘要，不含 Runtime 私有本地态）';
COMMENT ON COLUMN "public"."hasn_sync_events"."revision" IS 'Owner 维度单调递增 revision';
COMMENT ON COLUMN "public"."hasn_sync_events"."occurred_at" IS '事件发生时间';
COMMENT ON COLUMN "public"."hasn_sync_events"."expires_at" IS '事件保留到期时间（可空）';
COMMENT ON COLUMN "public"."hasn_sync_events"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_sync_events"."updated_time" IS '更新时间';
