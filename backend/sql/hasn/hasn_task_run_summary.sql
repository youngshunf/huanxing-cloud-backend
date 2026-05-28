-- =====================================================
-- HASN Task Run Summary 表
-- v2.1 云端任务运行摘要表
-- =====================================================
CREATE TABLE "public"."hasn_task_run_summary" (
  "id"                 bigserial PRIMARY KEY,
  "run_uuid"           varchar(64) NOT NULL,
  "task_uuid"          varchar(64) NOT NULL,
  "owner_id"           varchar(64) NOT NULL,
  "agent_id"           varchar(64) NOT NULL,
  "executor_node_id"   varchar(64),
  "session_id"         varchar(64),
  "scheduled_fire_at"  timestamptz(6),
  "dedupe_key"         varchar(200) NOT NULL,
  "status"             varchar(20) NOT NULL,
  "output_summary"     text,
  "error"              text,
  "deep_link"          varchar(500),
  "model"              varchar(100),
  "token_usage"        jsonb,
  "duration_ms"        integer,
  "started_at"         timestamptz(6),
  "finished_at"        timestamptz(6),
  "created_time"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"       timestamptz(6),

  CONSTRAINT "uq_hasn_task_run_summary_run_uuid" UNIQUE ("run_uuid"),
  CONSTRAINT "uq_hasn_task_run_summary_dedupe_key" UNIQUE ("dedupe_key")
);

CREATE INDEX "idx_hasn_task_run_summary_task" ON "public"."hasn_task_run_summary"("task_uuid");
CREATE INDEX "idx_hasn_task_run_summary_owner" ON "public"."hasn_task_run_summary"("owner_id");
CREATE INDEX "idx_hasn_task_run_summary_agent" ON "public"."hasn_task_run_summary"("agent_id");
CREATE INDEX "idx_hasn_task_run_summary_session" ON "public"."hasn_task_run_summary"("session_id");

COMMENT ON TABLE "public"."hasn_task_run_summary" IS 'v2.1 云端任务运行摘要表';
COMMENT ON COLUMN "public"."hasn_task_run_summary"."run_uuid" IS '端云稳定运行 UUID';
COMMENT ON COLUMN "public"."hasn_task_run_summary"."task_uuid" IS '端云稳定任务 UUID';
COMMENT ON COLUMN "public"."hasn_task_run_summary"."dedupe_key" IS '运行摘要幂等键';
COMMENT ON COLUMN "public"."hasn_task_run_summary"."output_summary" IS '输出摘要';
