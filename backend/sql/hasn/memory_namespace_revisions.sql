-- =====================================================
-- HASN 记忆命名空间权威 revision 表
-- =====================================================
CREATE TABLE "public"."memory_namespace_revisions" (
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

CREATE INDEX "idx_memory_namespace_revisions_updated"
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
