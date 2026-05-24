-- =====================================================
-- HASN Task 表
-- 任务定义表，支持 once/interval/cron 调度
-- 依赖 hasn_agents 表（agent_id 字段关联）
-- =====================================================
CREATE TABLE "public"."hasn_task" (
  "id"                    bigserial PRIMARY KEY,
  "owner_id"              varchar(64) NOT NULL,
  "agent_id"              varchar(64) NOT NULL,
  "name"                  varchar(200) NOT NULL,
  "description"           text,
  "prompt"                text NOT NULL,
  "skill_bundle_ids"      jsonb NOT NULL DEFAULT '[]',
  "skill_ids"             jsonb NOT NULL DEFAULT '[]',
  "workflow_id"           bigint,
  "enabled_toolsets"      jsonb,
  "context_from_task_id"  bigint,
  "schedule_type"         varchar(20) NOT NULL,
  "schedule_config"       jsonb NOT NULL,
  "schedule_display"      varchar(200),
  "enabled"               boolean NOT NULL DEFAULT true,
  "state"                 varchar(20) NOT NULL DEFAULT 'scheduled',
  "next_run_at"           timestamptz(6),
  "last_run_at"           timestamptz(6),
  "last_status"           varchar(20),
  "last_error"            text,
  "run_count"             integer NOT NULL DEFAULT 0,
  "repeat_times"          integer,
  "repeat_completed"      integer NOT NULL DEFAULT 0,
  "created_time"          timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"          timestamptz(6),
  "created_by"            varchar(64),

  CONSTRAINT "chk_hasn_task_schedule_type"
    CHECK ("schedule_type" IN ('once', 'interval', 'cron')),
  CONSTRAINT "chk_hasn_task_state"
    CHECK ("state" IN ('scheduled', 'paused', 'completed', 'error'))
);

CREATE INDEX "idx_hasn_task_next_run" ON "public"."hasn_task"("next_run_at")
  WHERE "enabled" = true;
CREATE INDEX "idx_hasn_task_owner" ON "public"."hasn_task"("owner_id");
CREATE INDEX "idx_hasn_task_agent" ON "public"."hasn_task"("agent_id");

COMMENT ON TABLE "public"."hasn_task" IS '任务定义表';
COMMENT ON COLUMN "public"."hasn_task"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_task"."owner_id" IS '任务归属 owner';
COMMENT ON COLUMN "public"."hasn_task"."agent_id" IS '执行 agent（必须有绑定 runtime）';
COMMENT ON COLUMN "public"."hasn_task"."name" IS '任务名称';
COMMENT ON COLUMN "public"."hasn_task"."description" IS '任务描述';
COMMENT ON COLUMN "public"."hasn_task"."prompt" IS '任务指令（支持模板变量）';
COMMENT ON COLUMN "public"."hasn_task"."skill_bundle_ids" IS 'Skill bundle 名称列表，如 ["backend-dev", "mlops"]';
COMMENT ON COLUMN "public"."hasn_task"."skill_ids" IS '单独 skill 名称列表，如 ["github-pr", "pytest"]';
COMMENT ON COLUMN "public"."hasn_task"."workflow_id" IS '工作流 ID（可选，未来扩展）';
COMMENT ON COLUMN "public"."hasn_task"."enabled_toolsets" IS '限制工具集 ["terminal", "file", "web"]（NULL=全部）';
COMMENT ON COLUMN "public"."hasn_task"."context_from_task_id" IS '链式任务：注入上次执行结果';
COMMENT ON COLUMN "public"."hasn_task"."schedule_type" IS '调度类型 (once:一次性:blue/interval:间隔:green/cron:定时:orange)';
COMMENT ON COLUMN "public"."hasn_task"."schedule_config" IS '调度配置 JSON: {expr: "0 9 * * *"} 或 {minutes: 60} 或 {run_at: "2026-05-23T09:00:00Z"}';
COMMENT ON COLUMN "public"."hasn_task"."schedule_display" IS '人类可读调度描述，如"每天 9:00"';
COMMENT ON COLUMN "public"."hasn_task"."enabled" IS '是否启用';
COMMENT ON COLUMN "public"."hasn_task"."state" IS '状态 (scheduled:已调度:blue/paused:已暂停:orange/completed:已完成:green/error:异常:red)';
COMMENT ON COLUMN "public"."hasn_task"."next_run_at" IS '下次执行时间';
COMMENT ON COLUMN "public"."hasn_task"."last_run_at" IS '上次执行时间';
COMMENT ON COLUMN "public"."hasn_task"."last_status" IS '上次执行状态 (ok:成功:green/error:错误:red/silent:静默:gray/timeout:超时:orange)';
COMMENT ON COLUMN "public"."hasn_task"."last_error" IS '上次错误信息';
COMMENT ON COLUMN "public"."hasn_task"."run_count" IS '总执行次数';
COMMENT ON COLUMN "public"."hasn_task"."repeat_times" IS '重复次数（NULL=永久，N=执行N次）';
COMMENT ON COLUMN "public"."hasn_task"."repeat_completed" IS '已重复执行次数';
COMMENT ON COLUMN "public"."hasn_task"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_task"."updated_time" IS '更新时间';
COMMENT ON COLUMN "public"."hasn_task"."created_by" IS '创建者';
