-- =====================================================
-- HASN 第三方渠道反向 onboarding pending intent 表（S1/S5 codegen 输入）
-- TTL 24h，业务实现留待 S5。
-- =====================================================
CREATE TABLE "public"."hasn_pending_intents" (
  "id"              bigserial PRIMARY KEY,
  "intent_id"       varchar(40) NOT NULL,
  "channel_type"    varchar(30) NOT NULL,
  "external_user_id" varchar(120) NOT NULL,
  "owner_id"        varchar(40),
  "agent_hasn_id"   varchar(40),
  "conversation_hint" varchar(120),
  "intent_type"     varchar(30) NOT NULL DEFAULT 'onboarding',
  "payload"         jsonb NOT NULL DEFAULT '{}',
  "status"          varchar(20) NOT NULL DEFAULT 'pending',
  "expires_at"      timestamptz(6) NOT NULL,
  "consumed_at"     timestamptz(6),
  "created_time"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"    timestamptz(6),
  CONSTRAINT "uq_hasn_pending_intents_intent" UNIQUE ("intent_id")
);

CREATE INDEX "idx_hasn_pending_intents_external" ON "public"."hasn_pending_intents" ("channel_type", "external_user_id", "status");
CREATE INDEX "idx_hasn_pending_intents_owner" ON "public"."hasn_pending_intents" ("owner_id") WHERE "owner_id" IS NOT NULL;
CREATE INDEX "idx_hasn_pending_intents_agent" ON "public"."hasn_pending_intents" ("agent_hasn_id") WHERE "agent_hasn_id" IS NOT NULL;
CREATE INDEX "idx_hasn_pending_intents_expires" ON "public"."hasn_pending_intents" ("expires_at");

COMMENT ON TABLE "public"."hasn_pending_intents" IS 'HASN 第三方渠道反向 onboarding pending intent 表';
COMMENT ON COLUMN "public"."hasn_pending_intents"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_pending_intents"."intent_id" IS 'Pending intent 唯一 ID (pi_{uuid})';
COMMENT ON COLUMN "public"."hasn_pending_intents"."channel_type" IS '渠道类型 (wechat:微信:green/feishu:飞书:blue/qq:QQ:cyan/webhook:Webhook:purple)';
COMMENT ON COLUMN "public"."hasn_pending_intents"."external_user_id" IS '第三方渠道用户 ID';
COMMENT ON COLUMN "public"."hasn_pending_intents"."owner_id" IS '已解析 Owner hasn_id（可空，onboarding 后回填）';
COMMENT ON COLUMN "public"."hasn_pending_intents"."agent_hasn_id" IS '目标 Agent hasn_id（可空）';
COMMENT ON COLUMN "public"."hasn_pending_intents"."conversation_hint" IS '渠道会话提示 ID';
COMMENT ON COLUMN "public"."hasn_pending_intents"."intent_type" IS '意图类型 (onboarding:反向登录:blue/message:待投递消息:green/channel_bind:渠道绑定:purple)';
COMMENT ON COLUMN "public"."hasn_pending_intents"."payload" IS '待处理载荷摘要';
COMMENT ON COLUMN "public"."hasn_pending_intents"."status" IS '状态 (pending:待处理:blue/consumed:已消费:green/expired:已过期:gray/revoked:已撤销:red)';
COMMENT ON COLUMN "public"."hasn_pending_intents"."expires_at" IS '过期时间（默认 TTL 24h，由业务层设置）';
COMMENT ON COLUMN "public"."hasn_pending_intents"."consumed_at" IS '消费时间';
COMMENT ON COLUMN "public"."hasn_pending_intents"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_pending_intents"."updated_time" IS '更新时间';
