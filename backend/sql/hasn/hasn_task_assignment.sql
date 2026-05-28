-- =====================================================
-- HASN Task Assignment 表
-- v2.1 任务执行归属表
-- =====================================================
CREATE TABLE "public"."hasn_task_assignment" (
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
  "updated_time"       timestamptz(6),

  CONSTRAINT "uq_hasn_task_assignment_task_uuid"
    UNIQUE ("task_uuid")
);

CREATE INDEX "idx_hasn_task_assignment_owner" ON "public"."hasn_task_assignment"("owner_id");
CREATE INDEX "idx_hasn_task_assignment_agent" ON "public"."hasn_task_assignment"("agent_id");
CREATE INDEX "idx_hasn_task_assignment_node" ON "public"."hasn_task_assignment"("executor_node_id");

COMMENT ON TABLE "public"."hasn_task_assignment" IS 'v2.1 任务执行归属表';
COMMENT ON COLUMN "public"."hasn_task_assignment"."task_uuid" IS '端云稳定任务 UUID';
COMMENT ON COLUMN "public"."hasn_task_assignment"."owner_id" IS '任务归属 owner';
COMMENT ON COLUMN "public"."hasn_task_assignment"."agent_id" IS '执行 Agent HASN ID';
COMMENT ON COLUMN "public"."hasn_task_assignment"."executor_kind" IS 'local_node/cloud_runtime_host/unresolved';
COMMENT ON COLUMN "public"."hasn_task_assignment"."executor_node_id" IS '执行节点 ID';
COMMENT ON COLUMN "public"."hasn_task_assignment"."binding_id" IS 'Runtime binding ID';
COMMENT ON COLUMN "public"."hasn_task_assignment"."assignment_state" IS 'assigned/unresolved/stale';
