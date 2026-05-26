-- =====================================================
-- HASN 记忆系统 - memory_events 表
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."memory_events" (
  "event_id"              varchar(40) PRIMARY KEY,
  "owner_id"              varchar(40) NOT NULL,
  "agent_id"              varchar(40),
  "subject_kind"          varchar(16) NOT NULL,
  "subject_id"            varchar(40) NOT NULL,
  "memory_layer"          varchar(16) NOT NULL DEFAULT 'episodic',
  "scope_kind"            varchar(16) NOT NULL DEFAULT 'conversation',
  "scope_id"              varchar(40) NOT NULL,
  "event_type"            varchar(40) NOT NULL,
  "summary"               text NOT NULL,
  "detail"                text,
  "related_peer_ids"      text NOT NULL DEFAULT '[]',
  "related_agent_ids"     text NOT NULL DEFAULT '[]',
  "source_conversation_id" varchar(40),
  "source_turn_ids"       text NOT NULL DEFAULT '[]',
  "source_refs_json"      text NOT NULL DEFAULT '[]',
  "occurred_at"           bigint NOT NULL,
  "created_at"            bigint NOT NULL,
  "embedding"             bytea,
  "deleted_at"            bigint,
  CHECK ("subject_kind" IN ('owner', 'agent_self', 'peer', 'world')),
  CHECK ("memory_layer" = 'episodic'),
  CHECK ("scope_kind" IN ('global', 'workspace', 'project', 'task', 'conversation', 'topic')),
  CHECK (
    ("subject_kind" = 'agent_self' AND "agent_id" IS NOT NULL)
    OR ("subject_kind" IN ('owner', 'peer', 'world') AND "agent_id" IS NULL)
  ),
  CHECK ("subject_kind" != 'world' OR "scope_kind" != 'global')
);

CREATE INDEX IF NOT EXISTS "idx_events_owner_time"
  ON "public"."memory_events"("owner_id", "subject_kind", "subject_id", "scope_kind", "scope_id", "occurred_at" DESC)
  WHERE "subject_kind" IN ('owner', 'peer', 'world');

CREATE INDEX IF NOT EXISTS "idx_events_agent_time"
  ON "public"."memory_events"("agent_id", "subject_id", "scope_kind", "scope_id", "occurred_at" DESC)
  WHERE "subject_kind" = 'agent_self';

CREATE INDEX IF NOT EXISTS "idx_events_type" ON "public"."memory_events"("owner_id", "event_type", "occurred_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_events_scope" ON "public"."memory_events"("owner_id", "scope_kind", "scope_id", "occurred_at" DESC);

COMMENT ON TABLE "public"."memory_events" IS 'HASN 记忆系统 - 时序事件';
COMMENT ON COLUMN "public"."memory_events"."event_id" IS 'Event ID';
COMMENT ON COLUMN "public"."memory_events"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."memory_events"."agent_id" IS 'Agent ID (仅 agent_self 时填)';
COMMENT ON COLUMN "public"."memory_events"."subject_kind" IS '主体类型';
COMMENT ON COLUMN "public"."memory_events"."subject_id" IS '主体 ID';
COMMENT ON COLUMN "public"."memory_events"."memory_layer" IS '记忆层次 (episodic)';
COMMENT ON COLUMN "public"."memory_events"."scope_kind" IS '作用域类型';
COMMENT ON COLUMN "public"."memory_events"."scope_id" IS '作用域 ID';
COMMENT ON COLUMN "public"."memory_events"."event_type" IS '事件类型';
COMMENT ON COLUMN "public"."memory_events"."summary" IS '摘要';
COMMENT ON COLUMN "public"."memory_events"."detail" IS '详情';
COMMENT ON COLUMN "public"."memory_events"."related_peer_ids" IS '相关 peer ID 列表';
COMMENT ON COLUMN "public"."memory_events"."related_agent_ids" IS '相关 agent ID 列表';
COMMENT ON COLUMN "public"."memory_events"."source_conversation_id" IS '来源会话 ID';
COMMENT ON COLUMN "public"."memory_events"."source_turn_ids" IS '来源 turn ID 列表';
COMMENT ON COLUMN "public"."memory_events"."source_refs_json" IS '来源引用 JSON';
COMMENT ON COLUMN "public"."memory_events"."occurred_at" IS '发生时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_events"."created_at" IS '创建时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_events"."embedding" IS 'Embedding 向量';
COMMENT ON COLUMN "public"."memory_events"."deleted_at" IS '删除时间 (epoch ms)';
