CREATE TABLE "public"."hasn_conversations" (
    "id"                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "type"                 varchar(10) NOT NULL DEFAULT 'direct',
    "relation_type"        varchar(20) DEFAULT 'social',
    "participant_a_id"     varchar(40) NOT NULL,
    "participant_b_id"     varchar(40),
    "participant_a_type"   varchar(10) NOT NULL DEFAULT 'human',
    "participant_b_type"   varchar(10) DEFAULT 'human',
    "trade_session_id"     uuid,
    "last_message_id"      int8,
    "last_message_at"      timestamptz(6),
    "last_message_preview" varchar(200),
    "last_message_from"    varchar(40),
    "message_count"        int4 NOT NULL DEFAULT 0,
    "created_time"         timestamptz(6) NOT NULL DEFAULT now(),
    "updated_time"         timestamptz(6)
);

COMMENT ON TABLE "public"."hasn_conversations" IS 'HASN 会话表';
COMMENT ON COLUMN "public"."hasn_conversations"."id" IS '会话 ID (UUID)';
COMMENT ON COLUMN "public"."hasn_conversations"."type" IS '会话类型 (direct:单聊/group:群聊)';
COMMENT ON COLUMN "public"."hasn_conversations"."relation_type" IS '关系类型 (social:社交/commerce:商业/service:履约/professional:专业/platform:平台)';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_a_id" IS '参与方 A 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_b_id" IS '参与方 B 的 hasn_id (群聊为 NULL)';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_a_type" IS '参与方 A 类型 (human:人类/agent:代理)';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_b_type" IS '参与方 B 类型 (human:人类/agent:代理)';
COMMENT ON COLUMN "public"."hasn_conversations"."trade_session_id" IS '关联交易会话 ID';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_id" IS '最后一条消息 ID';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_at" IS '最后消息时间';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_preview" IS '最后消息预览';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_from" IS '最后消息发送方 hasn_id';
COMMENT ON COLUMN "public"."hasn_conversations"."message_count" IS '消息总数';

CREATE INDEX "idx_hasn_conv_participant_a" ON "public"."hasn_conversations" ("participant_a_id");
CREATE INDEX "idx_hasn_conv_participant_b" ON "public"."hasn_conversations" ("participant_b_id");
CREATE INDEX "idx_hasn_conv_last_msg" ON "public"."hasn_conversations" ("participant_a_id", "last_message_at" DESC);
CREATE INDEX "idx_hasn_conv_relation" ON "public"."hasn_conversations" ("relation_type");
