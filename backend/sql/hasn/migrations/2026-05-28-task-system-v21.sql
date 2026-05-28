-- HASN task system v2.1 cloud authority migration
-- Safe to rerun: every schema addition uses IF NOT EXISTS where PostgreSQL supports it.

ALTER TABLE "public"."hasn_task"
  ADD COLUMN IF NOT EXISTS "system_prompt" text,
  ADD COLUMN IF NOT EXISTS "input_template" text,
  ADD COLUMN IF NOT EXISTS "skill_bundle_refs" jsonb NOT NULL DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS "skill_refs" jsonb NOT NULL DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS "workflow" jsonb NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS "timezone" varchar(64) NOT NULL DEFAULT 'Asia/Shanghai',
  ADD COLUMN IF NOT EXISTS "misfire_policy" varchar(20) NOT NULL DEFAULT 'skip',
  ADD COLUMN IF NOT EXISTS "catchup_limit" integer,
  ADD COLUMN IF NOT EXISTS "task_uuid" varchar(64),
  ADD COLUMN IF NOT EXISTS "executor_policy" varchar(32) NOT NULL DEFAULT 'local_node',
  ADD COLUMN IF NOT EXISTS "executor_node_id" varchar(64),
  ADD COLUMN IF NOT EXISTS "task_revision" bigint NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS "deleted_at" timestamptz(6);

ALTER TABLE "public"."hasn_task"
  ALTER COLUMN "state" TYPE varchar(40);

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'chk_hasn_task_state'
      AND conrelid = 'public.hasn_task'::regclass
  ) THEN
    ALTER TABLE "public"."hasn_task" DROP CONSTRAINT "chk_hasn_task_state";
  END IF;
END $$;

ALTER TABLE "public"."hasn_task"
  ADD CONSTRAINT "chk_hasn_task_state"
  CHECK ("state" IN (
    'scheduled',
    'paused',
    'completed',
    'error',
    'deleted',
    'waiting_for_runtime',
    'needs_package_resolution',
    'needs_skill_install'
  ));

DROP INDEX IF EXISTS "public"."uq_hasn_task_task_uuid";

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uq_hasn_task_task_uuid'
      AND conrelid = 'public.hasn_task'::regclass
  ) THEN
    ALTER TABLE "public"."hasn_task"
      ADD CONSTRAINT "uq_hasn_task_task_uuid" UNIQUE ("task_uuid");
  END IF;
END $$;
CREATE INDEX IF NOT EXISTS "idx_hasn_task_task_uuid" ON "public"."hasn_task"("task_uuid");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_executor_node" ON "public"."hasn_task"("executor_node_id");

CREATE TABLE IF NOT EXISTS "public"."hasn_task_assignment" (
  "id"                 bigserial PRIMARY KEY,
  "task_uuid"          varchar(64) NOT NULL,
  "owner_id"           varchar(64) NOT NULL,
  "agent_id"           varchar(64) NOT NULL,
  "executor_kind"      varchar(32) NOT NULL DEFAULT 'local_node',
  "executor_node_id"   varchar(64) NOT NULL DEFAULT '',
  "binding_id"         varchar(64),
  "assignment_state"   varchar(32) NOT NULL DEFAULT 'assigned',
  "resolved_at"        timestamptz(6),
  "stale_after"        timestamptz(6),
  "created_time"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"       timestamptz(6)
);

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uq_hasn_task_assignment_task_agent_node'
      AND conrelid = 'public.hasn_task_assignment'::regclass
  ) THEN
    ALTER TABLE "public"."hasn_task_assignment"
      DROP CONSTRAINT "uq_hasn_task_assignment_task_agent_node";
  END IF;
END $$;

DROP INDEX IF EXISTS "public"."uq_hasn_task_assignment_task_agent_node";

WITH ranked_assignments AS (
  SELECT
    ctid,
    ROW_NUMBER() OVER (
      PARTITION BY "task_uuid"
      ORDER BY "updated_time" DESC NULLS LAST, "id" DESC
    ) AS row_rank
  FROM "public"."hasn_task_assignment"
)
DELETE FROM "public"."hasn_task_assignment" a
USING ranked_assignments r
WHERE a.ctid = r.ctid
  AND r.row_rank > 1;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'uq_hasn_task_assignment_task_uuid'
      AND conrelid = 'public.hasn_task_assignment'::regclass
  ) THEN
    ALTER TABLE "public"."hasn_task_assignment"
      ADD CONSTRAINT "uq_hasn_task_assignment_task_uuid" UNIQUE ("task_uuid");
  END IF;
END $$;
CREATE INDEX IF NOT EXISTS "idx_hasn_task_assignment_owner" ON "public"."hasn_task_assignment"("owner_id");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_assignment_agent" ON "public"."hasn_task_assignment"("agent_id");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_assignment_node" ON "public"."hasn_task_assignment"("executor_node_id");

CREATE TABLE IF NOT EXISTS "public"."hasn_task_run_summary" (
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
  "updated_time"       timestamptz(6)
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_hasn_task_run_summary_run_uuid"
  ON "public"."hasn_task_run_summary"("run_uuid");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_hasn_task_run_summary_dedupe_key"
  ON "public"."hasn_task_run_summary"("dedupe_key");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_run_summary_task" ON "public"."hasn_task_run_summary"("task_uuid");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_run_summary_owner" ON "public"."hasn_task_run_summary"("owner_id");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_run_summary_agent" ON "public"."hasn_task_run_summary"("agent_id");
CREATE INDEX IF NOT EXISTS "idx_hasn_task_run_summary_session" ON "public"."hasn_task_run_summary"("session_id");

COMMENT ON TABLE "public"."hasn_task_assignment" IS 'v2.1 任务执行归属表';
COMMENT ON TABLE "public"."hasn_task_run_summary" IS 'v2.1 云端任务运行摘要表';
