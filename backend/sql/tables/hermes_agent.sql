CREATE TABLE "public"."hermes_agent" (
  "id" bigserial PRIMARY KEY,
  "agent_id" varchar(64) NOT NULL,
  "user_id" int8 NOT NULL,
  "agent_name" varchar(64) NOT NULL,
  "template" varchar(32) NOT NULL DEFAULT 'assistant',
  "timezone" varchar(64) NOT NULL DEFAULT 'Asia/Shanghai',
  "status" varchar(20) NOT NULL DEFAULT 'creating',
  "runtime_id" varchar(64),
  "runtime_profile_id" varchar(128),
  "profile_name" varchar(128),
  "llm_mode" varchar(16) NOT NULL DEFAULT 'platform',
  "llm_provider" varchar(32) NOT NULL DEFAULT 'openai_compatible',
  "llm_model" varchar(128),
  "gateway_status" varchar(20) NOT NULL DEFAULT 'stopped',
  "workspace_status" varchar(20) NOT NULL DEFAULT 'unknown',
  "sandbox_status" varchar(20) NOT NULL DEFAULT 'unknown',
  "channel_count" int4 NOT NULL DEFAULT 0,
  "last_active_at" timestamptz(6),
  "last_runtime_sync_at" timestamptz(6),
  "last_error_code" varchar(64),
  "last_error_message" varchar(500),
  "remark" varchar(512),
  "deleted_time" timestamptz(6),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE ("agent_id")
);

CREATE INDEX "idx_hermes_agent_user_status" ON "public"."hermes_agent" ("user_id", "status");
CREATE INDEX "idx_hermes_agent_runtime_profile" ON "public"."hermes_agent" ("runtime_profile_id");
CREATE INDEX "idx_hermes_agent_deleted_time" ON "public"."hermes_agent" ("deleted_time");
CREATE UNIQUE INDEX "uq_hermes_agent_user_name_active"
  ON "public"."hermes_agent" ("user_id", "agent_name")
  WHERE "deleted_time" IS NULL;

COMMENT ON TABLE "public"."hermes_agent" IS 'Hermes Agent 表';
COMMENT ON COLUMN "public"."hermes_agent"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hermes_agent"."agent_id" IS 'Agent 业务 ID';
COMMENT ON COLUMN "public"."hermes_agent"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."hermes_agent"."agent_name" IS 'Agent 名称';
COMMENT ON COLUMN "public"."hermes_agent"."template" IS '模板 ID (assistant:助手:blue/media-creator:媒体创作:purple/finance:财务:green/side-hustle:副业:orange/custom:自定义:gray)';
COMMENT ON COLUMN "public"."hermes_agent"."timezone" IS '时区';
COMMENT ON COLUMN "public"."hermes_agent"."status" IS 'Agent状态 (creating:创建中:orange/created:已创建:blue/ready:就绪:cyan/running:运行中:green/stopped:已停止:gray/error:异常:red/deleting:删除中:orange/deleted:已删除:gray)';
COMMENT ON COLUMN "public"."hermes_agent"."runtime_id" IS 'Runtime 实例 ID';
COMMENT ON COLUMN "public"."hermes_agent"."runtime_profile_id" IS 'Runtime Profile ID';
COMMENT ON COLUMN "public"."hermes_agent"."profile_name" IS 'Hermes profile 名';
COMMENT ON COLUMN "public"."hermes_agent"."llm_mode" IS 'LLM模式 (platform:平台托管:green/byok:用户自带:blue)';
COMMENT ON COLUMN "public"."hermes_agent"."llm_provider" IS 'LLM Provider';
COMMENT ON COLUMN "public"."hermes_agent"."llm_model" IS 'LLM 模型';
COMMENT ON COLUMN "public"."hermes_agent"."gateway_status" IS 'Gateway状态 (stopped:已停止:gray/starting:启动中:orange/running:运行中:green/restarting:重启中:orange/stopping:停止中:orange/unhealthy:不健康:red/error:异常:red)';
COMMENT ON COLUMN "public"."hermes_agent"."workspace_status" IS 'Workspace状态 (unknown:未知:gray/ready:就绪:green/active:运行中:blue/error:异常:red)';
COMMENT ON COLUMN "public"."hermes_agent"."sandbox_status" IS 'Sandbox状态 (unknown:未知:gray/ready:就绪:green/unprotected:未保护:orange/error:异常:red)';
COMMENT ON COLUMN "public"."hermes_agent"."channel_count" IS '已绑定渠道数';
COMMENT ON COLUMN "public"."hermes_agent"."last_active_at" IS '最近活跃时间';
COMMENT ON COLUMN "public"."hermes_agent"."last_runtime_sync_at" IS '最近 Runtime 同步时间';
COMMENT ON COLUMN "public"."hermes_agent"."last_error_code" IS '最近错误码';
COMMENT ON COLUMN "public"."hermes_agent"."last_error_message" IS '最近错误说明';
COMMENT ON COLUMN "public"."hermes_agent"."remark" IS '备注';
COMMENT ON COLUMN "public"."hermes_agent"."deleted_time" IS '软删除时间';
COMMENT ON COLUMN "public"."hermes_agent"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hermes_agent"."updated_time" IS '更新时间';
