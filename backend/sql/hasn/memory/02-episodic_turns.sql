-- =====================================================
-- HASN 记忆系统 - episodic_turns 表
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."episodic_turns" (
  "turn_id"          varchar(40) PRIMARY KEY,
  "conversation_id"  varchar(40) NOT NULL,
  "owner_id"         varchar(40) NOT NULL,
  "agent_id"         varchar(40) NOT NULL,
  "seq"              integer NOT NULL,
  "role"             varchar(16) NOT NULL,
  "sender_hasn_id"   varchar(40) NOT NULL,
  "content_text"     text NOT NULL,
  "content_tokens"   integer NOT NULL,
  "embedding"        bytea,
  "topic_chunk_id"   varchar(40),
  "created_at"       bigint NOT NULL,
  "deleted_at"       bigint,
  CHECK ("role" IN ('owner', 'agent', 'peer', 'system'))
);

CREATE INDEX IF NOT EXISTS "idx_turns_conv_seq" ON "public"."episodic_turns"("conversation_id", "seq");
CREATE INDEX IF NOT EXISTS "idx_turns_agent_time" ON "public"."episodic_turns"("agent_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_turns_owner_time" ON "public"."episodic_turns"("owner_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_turns_topic_chunk" ON "public"."episodic_turns"("topic_chunk_id");

COMMENT ON TABLE "public"."episodic_turns" IS 'HASN 记忆系统 - 原始对话 turn + embedding';
COMMENT ON COLUMN "public"."episodic_turns"."turn_id" IS 'Turn ID';
COMMENT ON COLUMN "public"."episodic_turns"."conversation_id" IS '会话 ID';
COMMENT ON COLUMN "public"."episodic_turns"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."episodic_turns"."agent_id" IS 'Agent ID';
COMMENT ON COLUMN "public"."episodic_turns"."seq" IS '会话内单调递增序号';
COMMENT ON COLUMN "public"."episodic_turns"."role" IS '角色 (owner/agent/peer/system)';
COMMENT ON COLUMN "public"."episodic_turns"."sender_hasn_id" IS '发送者 HASN ID';
COMMENT ON COLUMN "public"."episodic_turns"."content_text" IS '内容文本';
COMMENT ON COLUMN "public"."episodic_turns"."content_tokens" IS '内容 token 数';
COMMENT ON COLUMN "public"."episodic_turns"."embedding" IS 'Embedding 向量';
COMMENT ON COLUMN "public"."episodic_turns"."topic_chunk_id" IS '话题分片 ID';
COMMENT ON COLUMN "public"."episodic_turns"."created_at" IS '创建时间 (epoch ms)';
COMMENT ON COLUMN "public"."episodic_turns"."deleted_at" IS '删除时间 (epoch ms)';
