-- =====================================================
-- HASN 客户端上行 outbox 幂等/冲突表（S1 codegen 输入 + S4 业务写入）
-- =====================================================
CREATE TABLE "public"."hasn_sync_inbox_events" (
  "id"              bigserial PRIMARY KEY,
  "client_event_id" varchar(80) NOT NULL,
  "owner_id"        varchar(40) NOT NULL,
  "hasn_id"         varchar(40) NOT NULL,
  "node_id"         varchar(40) NOT NULL,
  "event_type"      varchar(50) NOT NULL,
  "payload"         jsonb NOT NULL DEFAULT '{}',
  "dedupe_key"      varchar(120),
  "status"          varchar(20) NOT NULL DEFAULT 'accepted',
  "server_revision" bigint,
  "conflict_reason" varchar(120),
  "received_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "created_time"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"    timestamptz(6),
  CONSTRAINT "uq_hasn_sync_inbox_client_event" UNIQUE ("owner_id", "node_id", "client_event_id")
);

CREATE INDEX "idx_hasn_sync_inbox_owner_status" ON "public"."hasn_sync_inbox_events" ("owner_id", "status", "received_at" DESC);
CREATE INDEX "idx_hasn_sync_inbox_hasn" ON "public"."hasn_sync_inbox_events" ("hasn_id", "received_at" DESC);
CREATE INDEX "idx_hasn_sync_inbox_dedupe" ON "public"."hasn_sync_inbox_events" ("owner_id", "dedupe_key") WHERE "dedupe_key" IS NOT NULL;

COMMENT ON TABLE "public"."hasn_sync_inbox_events" IS 'HASN 客户端上行 outbox 幂等/冲突表';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."client_event_id" IS '客户端事件 ID';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."owner_id" IS '事件所属 Owner hasn_id';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."hasn_id" IS '事件主体 hasn_id（Human 或 owned Agent）';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."node_id" IS '上报 Node ID';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."event_type" IS '事件类型 (ack:确认:green/read:已读:blue/edit:编辑:orange/recall:撤回:red/local_state:本地状态:gray)';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."payload" IS '客户端上行载荷（不得包含 workspace/endpoint/PID/CLI args/OAuth path）';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."dedupe_key" IS '业务幂等键';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."status" IS '处理状态 (accepted:已接收:blue/applied:已应用:green/conflict:冲突:orange/rejected:已拒绝:red)';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."server_revision" IS '对应服务端 revision';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."conflict_reason" IS '冲突原因';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."received_at" IS '服务端接收时间';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_sync_inbox_events"."updated_time" IS '更新时间';
