CREATE TABLE "public"."hermes_agent_operation" (
  "id" bigserial PRIMARY KEY,
  "operation_id" varchar(64) NOT NULL,
  "agent_id" varchar(64) NOT NULL,
  "user_id" int8 NOT NULL,
  "operation_type" varchar(32) NOT NULL,
  "operation_status" varchar(20) NOT NULL DEFAULT 'started',
  "idempotency_key" varchar(128),
  "runtime_request_id" varchar(128),
  "started_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "finished_at" timestamptz(6),
  "request_summary_json" jsonb,
  "response_summary_json" jsonb,
  "error_json" jsonb,
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE ("operation_id")
);

CREATE INDEX "idx_hermes_operation_agent" ON "public"."hermes_agent_operation" ("agent_id");
CREATE INDEX "idx_hermes_operation_user" ON "public"."hermes_agent_operation" ("user_id");
CREATE INDEX "idx_hermes_operation_status" ON "public"."hermes_agent_operation" ("operation_status");
CREATE INDEX "idx_hermes_operation_type" ON "public"."hermes_agent_operation" ("operation_type");

COMMENT ON TABLE "public"."hermes_agent_operation" IS 'Hermes Agent 操作记录表';
COMMENT ON COLUMN "public"."hermes_agent_operation"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hermes_agent_operation"."operation_id" IS '操作 ID';
COMMENT ON COLUMN "public"."hermes_agent_operation"."agent_id" IS 'Agent 业务 ID';
COMMENT ON COLUMN "public"."hermes_agent_operation"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."hermes_agent_operation"."operation_type" IS '操作类型 (create_agent:创建:blue/update_agent:更新:blue/delete_agent:删除:red/start_gateway:启动:green/restart_gateway:重启:orange/stop_gateway:停止:gray/bind_channel:绑定:purple/unbind_channel:解绑:orange/chat:对话:green/run:运行:cyan/sync_runtime:同步:blue)';
COMMENT ON COLUMN "public"."hermes_agent_operation"."operation_status" IS '操作状态 (started:已开始:blue/succeeded:成功:green/failed:失败:red/cancelled:已取消:gray)';
COMMENT ON COLUMN "public"."hermes_agent_operation"."idempotency_key" IS '幂等键';
COMMENT ON COLUMN "public"."hermes_agent_operation"."runtime_request_id" IS 'Runtime 请求 ID';
COMMENT ON COLUMN "public"."hermes_agent_operation"."started_at" IS '开始时间';
COMMENT ON COLUMN "public"."hermes_agent_operation"."finished_at" IS '结束时间';
COMMENT ON COLUMN "public"."hermes_agent_operation"."request_summary_json" IS '脱敏请求摘要 JSON';
COMMENT ON COLUMN "public"."hermes_agent_operation"."response_summary_json" IS '脱敏响应摘要 JSON';
COMMENT ON COLUMN "public"."hermes_agent_operation"."error_json" IS '错误 JSON';
COMMENT ON COLUMN "public"."hermes_agent_operation"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hermes_agent_operation"."updated_time" IS '更新时间';
