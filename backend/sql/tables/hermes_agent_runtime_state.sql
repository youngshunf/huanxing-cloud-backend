CREATE TABLE "public"."hermes_agent_runtime_state" (
  "id" bigserial PRIMARY KEY,
  "agent_id" varchar(64) NOT NULL,
  "runtime_id" varchar(64),
  "runtime_profile_id" varchar(128),
  "profile_name" varchar(128),
  "gateway_status" varchar(20) NOT NULL DEFAULT 'stopped',
  "gateway_restart_count" int4 NOT NULL DEFAULT 0,
  "gateway_started_at" timestamptz(6),
  "api_server_reachable" bool NOT NULL DEFAULT false,
  "terminal_backend" varchar(16) NOT NULL DEFAULT 'docker',
  "container_workspace" varchar(64) NOT NULL DEFAULT '/workspace',
  "host_workspace_display" varchar(256),
  "workspace_status" varchar(20) NOT NULL DEFAULT 'unknown',
  "workspace_file_count" int4 NOT NULL DEFAULT 0,
  "workspace_bytes_used" int8 NOT NULL DEFAULT 0,
  "workspace_last_write_at" timestamptz(6),
  "mount_policy" varchar(32) NOT NULL DEFAULT 'workspace_only',
  "network_policy" varchar(64) NOT NULL DEFAULT 'unknown',
  "network_ready" bool NOT NULL DEFAULT false,
  "runtime_snapshot" jsonb,
  "last_health_at" timestamptz(6),
  "last_error_code" varchar(64),
  "last_error_message" varchar(500),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE ("agent_id")
);

CREATE INDEX "idx_hermes_runtime_state_profile" ON "public"."hermes_agent_runtime_state" ("runtime_profile_id");
CREATE INDEX "idx_hermes_runtime_state_gateway" ON "public"."hermes_agent_runtime_state" ("gateway_status");

COMMENT ON TABLE "public"."hermes_agent_runtime_state" IS 'Hermes Agent Runtime 状态表';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."agent_id" IS 'Agent 业务 ID';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."runtime_id" IS 'Runtime 实例 ID';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."runtime_profile_id" IS 'Runtime Profile ID';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."profile_name" IS 'Hermes profile 名';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."gateway_status" IS 'Gateway状态 (stopped:已停止:gray/starting:启动中:orange/running:运行中:green/restarting:重启中:orange/stopping:停止中:orange/unhealthy:不健康:red/error:异常:red)';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."gateway_restart_count" IS 'Gateway 重启次数';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."gateway_started_at" IS 'Gateway 启动时间';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."api_server_reachable" IS 'API Server 是否可达';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."terminal_backend" IS 'Terminal backend (docker:Docker:blue/unknown:未知:gray)';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."container_workspace" IS '容器内工作区';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."host_workspace_display" IS '宿主机工作区脱敏展示路径';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."workspace_status" IS 'Workspace状态 (unknown:未知:gray/ready:就绪:green/active:运行中:blue/error:异常:red)';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."workspace_file_count" IS 'Workspace 文件数';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."workspace_bytes_used" IS 'Workspace 使用字节数';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."workspace_last_write_at" IS 'Workspace 最近写入时间';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."mount_policy" IS '挂载策略 (workspace_only:仅工作区:green/violation:存在违规:red)';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."network_policy" IS '网络策略 (unknown:未知:gray/public_outbound_internal_denied:公网可出内网阻断:green/unrestricted:不受限:orange/disabled:禁用:red)';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."network_ready" IS '网络策略是否就绪';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."runtime_snapshot" IS 'Runtime 脱敏快照 JSON';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."last_health_at" IS '最近健康检查时间';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."last_error_code" IS '最近错误码';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."last_error_message" IS '最近错误说明';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hermes_agent_runtime_state"."updated_time" IS '更新时间';
