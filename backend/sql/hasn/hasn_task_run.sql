-- =====================================================
-- HASN Task Run 表
-- 任务执行记录表
-- 依赖 hasn_task 表（task_id 外键）
-- =====================================================
CREATE TABLE "public"."hasn_task_run" (
  "id"              bigserial PRIMARY KEY,
  "task_id"         bigint NOT NULL,
  "agent_id"        varchar(64) NOT NULL,
  "runtime_node_id" varchar(64),
  "status"          varchar(20) NOT NULL DEFAULT 'pending',
  "started_at"      timestamptz(6),
  "finished_at"     timestamptz(6),
  "duration_ms"     integer,
  "prompt_snapshot" text,
  "output"          text,
  "error"           text,
  "model"           varchar(100),
  "token_usage"     jsonb,
  "create_time"     timestamptz(6) NOT NULL DEFAULT now(),

  CONSTRAINT "fk_hasn_task_run_task"
    FOREIGN KEY ("task_id") REFERENCES "public"."hasn_task"("id")
    ON DELETE CASCADE,
  CONSTRAINT "chk_hasn_task_run_status"
    CHECK ("status" IN ('pending', 'running', 'success', 'error', 'timeout', 'silent'))
);

CREATE INDEX "idx_hasn_task_run_task" ON "public"."hasn_task_run"("task_id");
CREATE INDEX "idx_hasn_task_run_status" ON "public"."hasn_task_run"("status");
CREATE INDEX "idx_hasn_task_run_create_time" ON "public"."hasn_task_run"("create_time" DESC);

COMMENT ON TABLE "public"."hasn_task_run" IS '任务执行记录表';
COMMENT ON COLUMN "public"."hasn_task_run"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_task_run"."task_id" IS '关联任务 ID';
COMMENT ON COLUMN "public"."hasn_task_run"."agent_id" IS '执行 agent ID';
COMMENT ON COLUMN "public"."hasn_task_run"."runtime_node_id" IS '执行的 hasn-node 节点 ID';
COMMENT ON COLUMN "public"."hasn_task_run"."status" IS '执行状态 (pending:待执行:blue/running:执行中:orange/success:成功:green/error:失败:red/timeout:超时:orange/silent:静默:gray)';
COMMENT ON COLUMN "public"."hasn_task_run"."started_at" IS '开始执行时间';
COMMENT ON COLUMN "public"."hasn_task_run"."finished_at" IS '完成时间';
COMMENT ON COLUMN "public"."hasn_task_run"."duration_ms" IS '执行耗时（毫秒）';
COMMENT ON COLUMN "public"."hasn_task_run"."prompt_snapshot" IS '执行时的完整 prompt（包含加载的 skill bundle 和 skill 内容）';
COMMENT ON COLUMN "public"."hasn_task_run"."output" IS 'Agent 最终输出';
COMMENT ON COLUMN "public"."hasn_task_run"."error" IS '错误信息';
COMMENT ON COLUMN "public"."hasn_task_run"."model" IS '使用的模型';
COMMENT ON COLUMN "public"."hasn_task_run"."token_usage" IS 'Token 消耗 {input_tokens, output_tokens, total_tokens}';
COMMENT ON COLUMN "public"."hasn_task_run"."create_time" IS '创建时间';
