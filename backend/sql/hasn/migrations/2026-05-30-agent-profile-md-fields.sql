-- =====================================================
-- Agent Profile 云端权威化 (P1)：hasn_agents 补 AGENTS.md / MEMORY.md / 模板版本
-- ADR: decisions/architecture/2026-05-30-agent-profile-cloud-authoritative.md §4 方案 A
-- 既有列复用：template_id / skills(jsonb) / soul_md / user_md / profile_source / profile_revision
-- =====================================================

ALTER TABLE "public"."hasn_agents"
  ADD COLUMN IF NOT EXISTS "agents_md"        text,
  ADD COLUMN IF NOT EXISTS "memory_md"        text,
  ADD COLUMN IF NOT EXISTS "template_version" varchar(40);

COMMENT ON COLUMN "public"."hasn_agents"."agents_md"        IS 'Agent AGENTS.md 内容（云端 Profile 配置源）';
COMMENT ON COLUMN "public"."hasn_agents"."memory_md"        IS 'Agent MEMORY.md 内容（Agent 自我演化记忆，云端 Profile 配置源）';
COMMENT ON COLUMN "public"."hasn_agents"."template_version" IS 'Agent 模板版本（创建时快照，可空）';
