-- =====================================================
-- HASN 记忆系统 - semantic_facts 表
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
