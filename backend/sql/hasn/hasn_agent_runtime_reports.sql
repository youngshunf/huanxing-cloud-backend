-- =====================================================
-- HASN Agent Runtime 脱敏摘要上报表（S1 codegen 输入 + S4 业务写入）
-- 不保存 workspace / endpoint / PID / CLI args / OAuth path。
-- =====================================================
CREATE TABLE "public"."hasn_agent_runtime_reports" (
  "id"                 bigserial PRIMARY KEY,
  "report_id"          varchar(40) NOT NULL,
  "owner_id"           varchar(40) NOT NULL,
  "agent_hasn_id"      varchar(40) NOT NULL,
  "node_id"            varchar(40) NOT NULL,
  "runtime_type"       varchar(30) NOT NULL,
  "runtime_status"     varchar(30) NOT NULL DEFAULT 'unknown',
  "adapter_registered" boolean NOT NULL DEFAULT false,
  "handle_available"   boolean NOT NULL DEFAULT false,
  "binding_id"         varchar(40),
  "runtime_revision"   bigint NOT NULL DEFAULT 1,
  "summary_json"       jsonb NOT NULL DEFAULT '{}',
  "last_seen_at"       timestamptz(6),
  "reported_at"        timestamptz(6) NOT NULL DEFAULT now(),
  "created_time"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"       timestamptz(6),
  CONSTRAINT "uq_hasn_agent_runtime_reports_report" UNIQUE ("report_id")
);

CREATE INDEX "idx_hasn_agent_runtime_reports_agent" ON "public"."hasn_agent_runtime_reports" ("owner_id", "agent_hasn_id", "reported_at" DESC);
CREATE INDEX "idx_hasn_agent_runtime_reports_node" ON "public"."hasn_agent_runtime_reports" ("node_id", "reported_at" DESC);
CREATE INDEX "idx_hasn_agent_runtime_reports_status" ON "public"."hasn_agent_runtime_reports" ("runtime_status", "reported_at" DESC);
CREATE INDEX "idx_hasn_agent_runtime_reports_binding" ON "public"."hasn_agent_runtime_reports" ("binding_id") WHERE "binding_id" IS NOT NULL;

COMMENT ON TABLE "public"."hasn_agent_runtime_reports" IS 'HASN Agent Runtime 脱敏摘要上报表';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."report_id" IS 'Runtime report 唯一 ID (rr_{uuid})';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."owner_id" IS 'Agent Owner hasn_id';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."agent_hasn_id" IS 'Agent hasn_id';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."node_id" IS '上报 Node ID';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."runtime_type" IS 'Runtime 类型 (claude_code:Claude Code:purple/codex:Codex:blue/hermes:Hermes:green/webhook:Webhook:orange/cloud_sdk:Cloud SDK:cyan/none:无:gray)';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."runtime_status" IS 'Runtime 状态 (online:在线:green/offline:离线:gray/unavailable:不可用:orange/error:错误:red/unknown:未知:gray)';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."adapter_registered" IS 'RuntimeAdapter 是否已注册';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."handle_available" IS 'RuntimeHandle 是否可调度';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."binding_id" IS '公共 Binding ID 摘要（可空）';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."runtime_revision" IS 'Runtime 摘要修订号';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."summary_json" IS '脱敏 Runtime Summary；禁止 workspace/endpoint/PID/CLI args/OAuth path';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."last_seen_at" IS 'Runtime 最后可见时间';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."reported_at" IS '上报时间';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_agent_runtime_reports"."updated_time" IS '更新时间';
