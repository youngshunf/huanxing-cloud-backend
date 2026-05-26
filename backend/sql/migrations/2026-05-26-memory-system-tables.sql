-- =====================================================
-- HASN 记忆系统数据库迁移
-- 创建时间: 2026-05-26
-- 说明: 创建记忆系统核心表
-- =====================================================

-- 1. memory_namespace_revisions (命名空间 revision 表)
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."memory_namespace_revisions" (
  "sync_scope_kind" varchar(16) NOT NULL,
  "sync_scope_id"   varchar(40) NOT NULL,
  "namespace"       varchar(40) NOT NULL,
  "revision"        bigint NOT NULL DEFAULT 0,
  "last_event_id"   varchar(40),
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "created_time"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"    timestamptz(6),
  PRIMARY KEY ("sync_scope_kind", "sync_scope_id", "namespace"),
  CHECK ("sync_scope_kind" IN ('owner', 'agent'))
);

CREATE INDEX IF NOT EXISTS "idx_memory_namespace_revisions_updated"
  ON "public"."memory_namespace_revisions" ("sync_scope_kind", "sync_scope_id", "updated_at" DESC);

COMMENT ON TABLE "public"."memory_namespace_revisions" IS 'HASN 记忆命名空间权威 revision 表';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."sync_scope_kind" IS '同步分区类型 (owner/agent)';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."sync_scope_id" IS '同步分区 ID（owner_id 或 agent_id）';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."namespace" IS '记忆命名空间（portraits/facts/tasks 等）';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."revision" IS '命名空间维度单调递增 revision';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."last_event_id" IS '最近一次触发该命名空间 revision 的服务端事件 ID';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."updated_at" IS '命名空间权威 revision 更新时间';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."memory_namespace_revisions"."updated_time" IS '更新时间';

-- 2. episodic_turns (原始对话 turn)
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

-- 3. semantic_facts (语义事实)
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."semantic_facts" (
  "fact_id"          varchar(40) PRIMARY KEY,
  "owner_id"         varchar(40) NOT NULL,
  "agent_id"         varchar(40),
  "subject_kind"     varchar(16) NOT NULL,
  "subject_id"       varchar(40) NOT NULL,
  "memory_layer"     varchar(16) NOT NULL DEFAULT 'semantic',
  "scope_kind"       varchar(16) NOT NULL DEFAULT 'global',
  "scope_id"         varchar(40) NOT NULL,
  "predicate"        text NOT NULL,
  "object_json"      text NOT NULL,
  "confidence"       double precision NOT NULL,
  "status"           varchar(16) NOT NULL DEFAULT 'active',
  "superseded_by"    varchar(40),
  "source_turn_ids"  text NOT NULL DEFAULT '[]',
  "source_refs_json" text NOT NULL DEFAULT '[]',
  "rationale"        text,
  "created_at"       bigint NOT NULL,
  "updated_at"       bigint NOT NULL,
  CHECK ("subject_kind" IN ('owner', 'agent_self', 'peer', 'world')),
  CHECK ("memory_layer" = 'semantic'),
  CHECK ("scope_kind" IN ('global', 'workspace', 'project', 'task', 'conversation', 'topic')),
  CHECK (
    ("subject_kind" = 'agent_self' AND "agent_id" IS NOT NULL)
    OR ("subject_kind" IN ('owner', 'peer', 'world') AND "agent_id" IS NULL)
  ),
  CHECK ("subject_kind" != 'world' OR "scope_kind" != 'global')
);

CREATE INDEX IF NOT EXISTS "idx_facts_owner_active"
  ON "public"."semantic_facts"("owner_id", "subject_kind", "subject_id", "scope_kind", "scope_id", "predicate")
  WHERE "status" = 'active' AND "subject_kind" IN ('owner', 'peer', 'world');

CREATE INDEX IF NOT EXISTS "idx_facts_agent_active"
  ON "public"."semantic_facts"("agent_id", "subject_id", "scope_kind", "scope_id", "predicate")
  WHERE "status" = 'active' AND "subject_kind" = 'agent_self';

CREATE INDEX IF NOT EXISTS "idx_facts_scope_active"
  ON "public"."semantic_facts"("owner_id", "scope_kind", "scope_id", "updated_at" DESC)
  WHERE "status" = 'active';

COMMENT ON TABLE "public"."semantic_facts" IS 'HASN 记忆系统 - 语义事实';
COMMENT ON COLUMN "public"."semantic_facts"."fact_id" IS 'Fact ID';
COMMENT ON COLUMN "public"."semantic_facts"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."semantic_facts"."agent_id" IS 'Agent ID (仅 agent_self 时填)';
COMMENT ON COLUMN "public"."semantic_facts"."subject_kind" IS '主体类型 (owner/agent_self/peer/world)';
COMMENT ON COLUMN "public"."semantic_facts"."subject_id" IS '主体 ID';
COMMENT ON COLUMN "public"."semantic_facts"."memory_layer" IS '记忆层次 (semantic)';
COMMENT ON COLUMN "public"."semantic_facts"."scope_kind" IS '作用域类型';
COMMENT ON COLUMN "public"."semantic_facts"."scope_id" IS '作用域 ID';
COMMENT ON COLUMN "public"."semantic_facts"."predicate" IS '谓词';
COMMENT ON COLUMN "public"."semantic_facts"."object_json" IS '对象 JSON';
COMMENT ON COLUMN "public"."semantic_facts"."confidence" IS '置信度';
COMMENT ON COLUMN "public"."semantic_facts"."status" IS '状态 (active/superseded/disputed/withdrawn)';
COMMENT ON COLUMN "public"."semantic_facts"."superseded_by" IS '被替代的 fact_id';
COMMENT ON COLUMN "public"."semantic_facts"."source_turn_ids" IS '来源 turn ID 列表';
COMMENT ON COLUMN "public"."semantic_facts"."source_refs_json" IS '来源引用 JSON';
COMMENT ON COLUMN "public"."semantic_facts"."rationale" IS '理由';
COMMENT ON COLUMN "public"."semantic_facts"."created_at" IS '创建时间 (epoch ms)';
COMMENT ON COLUMN "public"."semantic_facts"."updated_at" IS '更新时间 (epoch ms)';

-- 4. memory_events (时序事件)
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

-- 5. memory_extraction_jobs (提取任务)
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."memory_extraction_jobs" (
  "job_id"                varchar(40) PRIMARY KEY,
  "agent_id"              varchar(40) NOT NULL,
  "owner_id"              varchar(40) NOT NULL,
  "conversation_id"       varchar(40) NOT NULL,
  "window_start_msg_id"   varchar(40) NOT NULL,
  "window_end_msg_id"     varchar(40) NOT NULL,
  "trigger_reason"        varchar(40) NOT NULL,
  "source_dispatch_mode"  varchar(16),
  "status"                varchar(16) NOT NULL,
  "attempt"               integer NOT NULL DEFAULT 0,
  "scheduled_at"          bigint NOT NULL,
  "started_at"            bigint,
  "completed_at"          bigint,
  "error_code"            varchar(40),
  CHECK ("status" IN ('queued', 'running', 'succeeded', 'failed', 'skipped')),
  UNIQUE ("agent_id", "conversation_id", "window_end_msg_id", "trigger_reason")
);

CREATE INDEX IF NOT EXISTS "idx_jobs_status_sched"
  ON "public"."memory_extraction_jobs"("status", "scheduled_at");

COMMENT ON TABLE "public"."memory_extraction_jobs" IS 'HASN 记忆系统 - 提取任务';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."job_id" IS 'Job ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."agent_id" IS 'Agent ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."conversation_id" IS '会话 ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."window_start_msg_id" IS '窗口起始消息 ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."window_end_msg_id" IS '窗口结束消息 ID';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."trigger_reason" IS '触发原因';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."source_dispatch_mode" IS '来源 dispatch 模式';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."status" IS '状态 (queued/running/succeeded/failed/skipped)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."attempt" IS '尝试次数';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."scheduled_at" IS '调度时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."started_at" IS '开始时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."completed_at" IS '完成时间 (epoch ms)';
COMMENT ON COLUMN "public"."memory_extraction_jobs"."error_code" IS '错误码';
