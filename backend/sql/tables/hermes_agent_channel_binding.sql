CREATE TABLE "public"."hermes_agent_channel_binding" (
  "id" bigserial PRIMARY KEY,
  "binding_id" varchar(64) NOT NULL,
  "agent_id" varchar(64) NOT NULL,
  "user_id" int8 NOT NULL,
  "channel" varchar(20) NOT NULL,
  "bind_mode" varchar(20) NOT NULL DEFAULT 'qr',
  "status" varchar(32) NOT NULL DEFAULT 'unbound',
  "display_name" varchar(64),
  "bound_account_display" varchar(128),
  "runtime_session_id" varchar(128),
  "expires_at" timestamptz(6),
  "metadata_json" jsonb,
  "last_error_code" varchar(64),
  "last_error_message" varchar(500),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE ("binding_id"),
  UNIQUE ("agent_id", "channel")
);

CREATE INDEX "idx_hermes_channel_user" ON "public"."hermes_agent_channel_binding" ("user_id");
CREATE INDEX "idx_hermes_channel_status" ON "public"."hermes_agent_channel_binding" ("status");
CREATE INDEX "idx_hermes_channel_session" ON "public"."hermes_agent_channel_binding" ("runtime_session_id");

COMMENT ON TABLE "public"."hermes_agent_channel_binding" IS 'Hermes Agent 渠道绑定表';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."binding_id" IS '绑定业务 ID';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."agent_id" IS 'Agent 业务 ID';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."channel" IS '渠道 (feishu:飞书:blue/weixin:微信:green/qq:QQ:purple)';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."bind_mode" IS '绑定方式 (qr:扫码:green/manual:手动:blue/webhook:回调:orange)';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."status" IS '状态 (unbound:未绑:gray/created:创建:blue/qr_ready:QR:blue/waiting_scan:待扫:orange/scanned:已扫:orange/confirmed:确认:blue/writing_config:写:orange/restarting_gateway:重启:orange/testing_connection:测试:blue/bound:绑定:green/expired:过期:gray/failed:失败:red/cancelled:取消:gray)';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."display_name" IS '渠道展示名';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."bound_account_display" IS '脱敏绑定账号';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."runtime_session_id" IS 'Runtime 绑定 Session ID';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."expires_at" IS '绑定 Session 过期时间';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."metadata_json" IS '脱敏元数据 JSON';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."last_error_code" IS '最近错误码';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."last_error_message" IS '最近错误说明';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hermes_agent_channel_binding"."updated_time" IS '更新时间';
