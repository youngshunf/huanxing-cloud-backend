-- =====================================================
-- HASN Channel Binding 表（S1/S5 codegen 输入）
-- =====================================================
CREATE TABLE "public"."hasn_channel_bindings" (
  "id"               bigserial PRIMARY KEY,
  "binding_id"       varchar(40) NOT NULL,
  "owner_id"         varchar(40) NOT NULL,
  "agent_hasn_id"    varchar(40),
  "channel_type"     varchar(30) NOT NULL,
  "external_user_id" varchar(120) NOT NULL,
  "external_chat_id" varchar(120),
  "display_name"     varchar(120),
  "binding_scope"    varchar(30) NOT NULL DEFAULT 'owner',
  "status"           varchar(20) NOT NULL DEFAULT 'active',
  "policy_json"      jsonb NOT NULL DEFAULT '{}',
  "last_inbound_at"  timestamptz(6),
  "last_outbound_at" timestamptz(6),
  "revoked_at"       timestamptz(6),
  "created_time"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"     timestamptz(6),
  CONSTRAINT "uq_hasn_channel_bindings_binding" UNIQUE ("binding_id"),
  CONSTRAINT "uq_hasn_channel_bindings_external" UNIQUE ("channel_type", "external_user_id", "external_chat_id")
);

CREATE INDEX "idx_hasn_channel_bindings_owner" ON "public"."hasn_channel_bindings" ("owner_id", "status");
CREATE INDEX "idx_hasn_channel_bindings_agent" ON "public"."hasn_channel_bindings" ("agent_hasn_id") WHERE "agent_hasn_id" IS NOT NULL;
CREATE INDEX "idx_hasn_channel_bindings_channel" ON "public"."hasn_channel_bindings" ("channel_type", "status");

COMMENT ON TABLE "public"."hasn_channel_bindings" IS 'HASN Channel Binding 表';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."binding_id" IS 'Channel Binding 唯一 ID (cb_{uuid})';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."owner_id" IS 'Owner hasn_id';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."agent_hasn_id" IS '绑定 Agent hasn_id（可空表示 Owner 级绑定）';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."channel_type" IS '渠道类型 (wechat:微信:green/feishu:飞书:blue/qq:QQ:cyan/webhook:Webhook:purple)';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."external_user_id" IS '第三方渠道用户 ID';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."external_chat_id" IS '第三方渠道会话/群 ID（可空）';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."display_name" IS '渠道侧展示名';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."binding_scope" IS '绑定范围 (owner:Owner:blue/agent:Agent:green/group:群聊:purple)';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."status" IS '状态 (active:生效中:green/revoked:已吊销:red/deleted:已删除:gray)';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."policy_json" IS '渠道策略摘要';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."last_inbound_at" IS '最近入站时间';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."last_outbound_at" IS '最近出站时间';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."revoked_at" IS '吊销时间';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_channel_bindings"."updated_time" IS '更新时间';
