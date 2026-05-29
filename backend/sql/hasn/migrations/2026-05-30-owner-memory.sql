-- =====================================================
-- Owner 记忆合并 (P4)：owner 维度记忆权威表 + 各 Agent 贡献表
-- ADR: decisions/architecture/2026-05-30-agent-profile-cloud-authoritative.md §4/§5.4
-- 各 Agent 上传 USER.md 观察 -> contribution(pending) -> 云端 LLM 合并压缩 ->
-- owner_memory(version++) -> 回写每个 Agent hasn_agents.user_md + bump profile_revision
-- =====================================================

CREATE TABLE IF NOT EXISTS "public"."hasn_owner_memory" (
  "id"               bigserial PRIMARY KEY,
  "owner_id"         varchar(40) NOT NULL,
  "content"          text,
  "version"          int NOT NULL DEFAULT 1,
  "token_count"      int,
  "last_merged_time" timestamptz(6),
  "created_time"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"     timestamptz(6),
  CONSTRAINT "uq_hasn_owner_memory_owner_id" UNIQUE ("owner_id")
);

COMMENT ON TABLE  "public"."hasn_owner_memory"                    IS 'Owner 记忆（权威，owner 维度）';
COMMENT ON COLUMN "public"."hasn_owner_memory"."owner_id"         IS 'Owner 的 hasn_id（hasn_humans.hasn_id）';
COMMENT ON COLUMN "public"."hasn_owner_memory"."content"          IS '合并压缩后的 USER.md（下发给各 Agent）';
COMMENT ON COLUMN "public"."hasn_owner_memory"."version"          IS '记忆版本（每次合并 +1）';
COMMENT ON COLUMN "public"."hasn_owner_memory"."token_count"      IS '压缩后内容估算 token 数';
COMMENT ON COLUMN "public"."hasn_owner_memory"."last_merged_time" IS '最后合并时间';

CREATE TABLE IF NOT EXISTS "public"."hasn_owner_memory_contribution" (
  "id"                  bigserial PRIMARY KEY,
  "owner_id"            varchar(40) NOT NULL,
  "agent_hasn_id"       varchar(40) NOT NULL,
  "content"             text,
  "status"              varchar(20) NOT NULL DEFAULT 'pending',
  "merged_into_version" int,
  "created_time"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"        timestamptz(6)
);

CREATE INDEX IF NOT EXISTS "idx_hasn_owner_memory_contribution_owner_status"
  ON "public"."hasn_owner_memory_contribution" ("owner_id", "status", "id");

COMMENT ON TABLE  "public"."hasn_owner_memory_contribution"                       IS 'Owner 记忆贡献（各 Agent 上传，待合并）';
COMMENT ON COLUMN "public"."hasn_owner_memory_contribution"."owner_id"            IS 'Owner 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_owner_memory_contribution"."agent_hasn_id"       IS '上传 Agent 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_owner_memory_contribution"."content"             IS 'Agent 观察到的主人信息片段（本地 USER.md 增量）';
COMMENT ON COLUMN "public"."hasn_owner_memory_contribution"."status"              IS '状态 (pending:待合并:orange/merged:已合并:green/discarded:丢弃:gray)';
COMMENT ON COLUMN "public"."hasn_owner_memory_contribution"."merged_into_version" IS '合并进的 owner_memory 版本';
