-- =====================================================
-- HASN 会话表（统一承载单聊 + 群聊）
-- type='direct': 单聊，使用 participant_a/b 字段
-- type='group':  群聊，使用 group_* 字段，成员在 hasn_group_members
-- =====================================================
CREATE TABLE "public"."hasn_conversations" (
  "id"                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "type"                 varchar(10) NOT NULL DEFAULT 'direct',
  "relation_type"        varchar(20) DEFAULT 'social',

  -- ===== 单聊字段 (type='direct') =====
  "participant_a_id"     varchar(40) NOT NULL,
  "participant_b_id"     varchar(40),
  "participant_a_type"   varchar(10) NOT NULL DEFAULT 'human',
  "participant_b_type"   varchar(10) DEFAULT 'human',
  "trade_session_id"     uuid,

  -- ===== 群聊字段 (type='group') =====
  "group_id"             varchar(20),
  "group_name"           varchar(100),
  "group_description"    text,
  "group_avatar_url"     varchar(500),
  "group_owner_id"       varchar(40),
  "agent_policy"         varchar(20) NOT NULL DEFAULT 'free',
  "join_policy"          varchar(20) NOT NULL DEFAULT 'invite_only',
  "max_members"          int4 NOT NULL DEFAULT 500,
  "allow_invite"         boolean NOT NULL DEFAULT true,
  "mute_all"             boolean NOT NULL DEFAULT false,
  "member_count"         int4 NOT NULL DEFAULT 0,

  -- ===== 通用字段 =====
  "last_message_id"      int8,
  "last_message_at"      timestamptz(6),
  "last_message_preview" varchar(200),
  "last_message_from"    varchar(40),
  "message_count"        int4 NOT NULL DEFAULT 0,
  "status"               varchar(20) NOT NULL DEFAULT 'active',
  "created_time"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"         timestamptz(6)
);

CREATE INDEX "idx_hasn_conv_participant_a" ON "public"."hasn_conversations" ("participant_a_id");
CREATE INDEX "idx_hasn_conv_participant_b" ON "public"."hasn_conversations" ("participant_b_id");
CREATE INDEX "idx_hasn_conv_last_msg" ON "public"."hasn_conversations" ("participant_a_id", "last_message_at" DESC);
CREATE INDEX "idx_hasn_conv_relation" ON "public"."hasn_conversations" ("relation_type");
CREATE INDEX "idx_hasn_conv_type" ON "public"."hasn_conversations" ("type");
CREATE UNIQUE INDEX "idx_hasn_conv_group_id" ON "public"."hasn_conversations" ("group_id") WHERE group_id IS NOT NULL;
CREATE INDEX "idx_hasn_conv_group_owner" ON "public"."hasn_conversations" ("group_owner_id") WHERE type = 'group';
CREATE INDEX "idx_hasn_conv_status" ON "public"."hasn_conversations" ("status");

COMMENT ON TABLE "public"."hasn_conversations" IS 'HASN 会话表';
COMMENT ON COLUMN "public"."hasn_conversations"."id" IS '会话 ID (UUID)';
COMMENT ON COLUMN "public"."hasn_conversations"."type" IS '会话类型 (direct:单聊:blue/group:群聊:green)';
COMMENT ON COLUMN "public"."hasn_conversations"."relation_type" IS '关系类型 (social:社交:blue/commerce:商业:orange/service:履约:green/professional:专业:purple/platform:平台:cyan)';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_a_id" IS '参与方 A hasn_id（单聊必填，群聊=创建者）';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_b_id" IS '参与方 B hasn_id（单聊必填，群聊为 NULL）';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_a_type" IS '参与方 A 类型 (human:人类:blue/agent:代理:green)';
COMMENT ON COLUMN "public"."hasn_conversations"."participant_b_type" IS '参与方 B 类型 (human:人类:blue/agent:代理:green)';
COMMENT ON COLUMN "public"."hasn_conversations"."trade_session_id" IS '关联交易会话 ID';
COMMENT ON COLUMN "public"."hasn_conversations"."group_id" IS '群组公开标识（格式: g:500001，type=group 时有值）';
COMMENT ON COLUMN "public"."hasn_conversations"."group_name" IS '群名称（type=group 时有值）';
COMMENT ON COLUMN "public"."hasn_conversations"."group_description" IS '群描述（type=group 时有值）';
COMMENT ON COLUMN "public"."hasn_conversations"."group_avatar_url" IS '群头像 URL（type=group 时有值）';
COMMENT ON COLUMN "public"."hasn_conversations"."group_owner_id" IS '群主 hasn_id（type=group 时有值）';
COMMENT ON COLUMN "public"."hasn_conversations"."agent_policy" IS 'Agent 发言策略 (free:自由:green/mention_only:@提及:blue/silent:静默:gray/no_agent:禁止:red)';
COMMENT ON COLUMN "public"."hasn_conversations"."join_policy" IS '加入策略 (open:开放:green/invite_only:仅邀请:blue/approval:需审核:orange)';
COMMENT ON COLUMN "public"."hasn_conversations"."max_members" IS '最大成员数';
COMMENT ON COLUMN "public"."hasn_conversations"."allow_invite" IS '成员是否可邀请';
COMMENT ON COLUMN "public"."hasn_conversations"."mute_all" IS '全员禁言';
COMMENT ON COLUMN "public"."hasn_conversations"."member_count" IS '当前成员数';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_id" IS '最后一条消息 ID';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_at" IS '最后消息时间';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_preview" IS '最后消息预览';
COMMENT ON COLUMN "public"."hasn_conversations"."last_message_from" IS '最后消息发送方 hasn_id';
COMMENT ON COLUMN "public"."hasn_conversations"."message_count" IS '消息总数';
COMMENT ON COLUMN "public"."hasn_conversations"."status" IS '状态 (active:活跃:green/archived:已归档:gray/disbanded:已解散:red)';
COMMENT ON COLUMN "public"."hasn_conversations"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_conversations"."updated_time" IS '更新时间';
