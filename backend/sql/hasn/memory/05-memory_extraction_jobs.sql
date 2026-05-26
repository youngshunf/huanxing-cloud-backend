-- =====================================================
-- HASN 记忆系统 - memory_extraction_jobs 表
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."memory_extraction_jobs" (
  "job_id"                varchar(40) PRIMARY KEY,
  "agent_id"              varchar(40) NOT NULL,
  "owner_id"              varchar(40) NOT NULL,
  "conversation_id"       varchar(40) NOT NULL,
  "window_start_msg_id"   varchar(40) NOT NULL,
  "window_end_msg_id"     varchar(40) NOT NULL,
  "trigger_reason"        varchar(40) NOT NULL,
  "source_dispatch_mode"  varchar(16),
  "status"                varchar(16) NOT NULL,
  "attempt"               integer NOT NULL DEFAULT 0,
  "scheduled_at"          bigint NOT NULL,
  "started_at"            bigint,
  "completed_at"          bigint,
  "error_code"            varchar(40),
  CHECK ("status" IN ('queued', 'running', 'succeeded', 'failed', 'skipped')),
  UNIQUE ("agent_id", "conversation_id", "window_end_msg_id", "trigger_reason")
);

CREATE INDEX IF NOT EXISTS "idx_jobs_status_sched"
  ON "public"."memory_extraction_jobs"("status", "scheduled_at");

COMMENT ON TABLE "public"."memory_extraction_jobs" IS 'HASN 记忆系统 - 提取任务';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."job_id" IS 'Job ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."agent_id" IS 'Agent ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."conversation_id" IS '会话 ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."window_start_msg_id" IS '窗口起始消息 ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."window_end_msg_id" IS '窗口结束消息 ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."trigger_reason" IS '触发原因';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."source_dispatch_mode" IS '来源 dispatch 模式';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."status" IS '状态 (queued/running/succeeded/failed/skipped)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."attempt" IS '尝试次数';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."scheduled_at" IS '调度时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."started_at" IS '开始时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."completed_at" IS '完成时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."error_code" IS '错误码';
