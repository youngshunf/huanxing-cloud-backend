-- =====================================================
-- HASN Agent 表
-- 对应协议: Layer 1 §1.2 Agent 实体 + §4.2 AgentCard
-- 注意：依赖 hasn_clients 表 (home_client_id 外键)，必须先建 hasn_clients
-- =====================================================
CREATE TABLE "public"."hasn_agents" (
  "id"             bigserial PRIMARY KEY,
  "hasn_id"        varchar(40) NOT NULL,
  "star_id"        varchar(40) NOT NULL,
  "owner_id"       varchar(40) NOT NULL,
  "display_name"   varchar(100) NOT NULL,
  "agent_name"     varchar(30) NOT NULL,
  "description"    text,
  "bio"            text,
  "profile_json"   jsonb NOT NULL DEFAULT '{}',
  "avatar"         varchar(500),
  "type"           varchar(20) NOT NULL DEFAULT 'cloud',
  "role"           varchar(20) NOT NULL DEFAULT 'primary',
  "server_id"      varchar(50),
  "node_id"        varchar(40),
  "home_client_id" int8,
  "api_key_hash"   varchar(64) NOT NULL,
  "capability_summary_json" jsonb NOT NULL DEFAULT '{}',
  "capability_revision" bigint NOT NULL DEFAULT 1,
  "profile_revision" bigint NOT NULL DEFAULT 1,
  "policy_revision" bigint NOT NULL DEFAULT 1,
  "sync_revision" bigint NOT NULL DEFAULT 1,
  "runtime_summary_json" jsonb NOT NULL DEFAULT '{}',
  "tags"           jsonb NOT NULL DEFAULT '[]',
  "capability_set_id" varchar(80),
  "persona_ref"    varchar(120),
  "status"         varchar(20) NOT NULL DEFAULT 'active',
  "created_via"    varchar(20) NOT NULL DEFAULT 'guardian',
  "created_time"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"   timestamptz(6),
  UNIQUE("hasn_id"),
  UNIQUE("star_id"),
  CONSTRAINT "fk_hasn_agents_home_client"
    FOREIGN KEY ("home_client_id") REFERENCES "public"."hasn_clients"("id")
    ON DELETE SET NULL
);

CREATE INDEX "idx_hasn_agents_owner" ON "public"."hasn_agents" ("owner_id");
CREATE INDEX "idx_hasn_agents_server" ON "public"."hasn_agents" ("server_id");
CREATE INDEX "idx_hasn_agents_status" ON "public"."hasn_agents" ("status");
CREATE INDEX "idx_hasn_agents_node" ON "public"."hasn_agents" ("node_id") WHERE "node_id" IS NOT NULL;
CREATE INDEX "idx_hasn_agents_sync_revision" ON "public"."hasn_agents" ("sync_revision");

COMMENT ON TABLE "public"."hasn_agents" IS 'HASN Agent 表';
COMMENT ON COLUMN "public"."hasn_agents"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_agents"."hasn_id" IS 'HASN Agent 唯一标识（格式: a_{uuid}）';
COMMENT ON COLUMN "public"."hasn_agents"."star_id" IS 'Agent 唤星号（如: 100001#star）';
COMMENT ON COLUMN "public"."hasn_agents"."owner_id" IS '所属 Human 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_agents"."display_name" IS 'Agent 显示名（支持中文，对外展示）';
COMMENT ON COLUMN "public"."hasn_agents"."agent_name" IS 'Agent 标识名';
COMMENT ON COLUMN "public"."hasn_agents"."description" IS 'Agent 描述';
COMMENT ON COLUMN "public"."hasn_agents"."bio" IS 'Agent Profile 简介（迁移期默认回填自 description）';
COMMENT ON COLUMN "public"."hasn_agents"."profile_json" IS 'Agent Profile 扩展摘要（不得存 Runtime 私有本地态）';
COMMENT ON COLUMN "public"."hasn_agents"."avatar" IS '头像（与 sys_user.avatar 对齐）';
COMMENT ON COLUMN "public"."hasn_agents"."type" IS 'Agent 类型 (cloud:云端:blue/local:本地:green)';
COMMENT ON COLUMN "public"."hasn_agents"."role" IS 'Agent 角色 (primary:主要:blue/specialist:专家:green/service:服务:orange)';
COMMENT ON COLUMN "public"."hasn_agents"."server_id" IS '云端 Agent 所在服务器 ID';
COMMENT ON COLUMN "public"."hasn_agents"."node_id" IS 'Agent 当前归属 Node ID（身份摘要，不含 endpoint/workspace/PID 等私有态）';
COMMENT ON COLUMN "public"."hasn_agents"."home_client_id" IS '本地 Agent 归属客户端 ID';
COMMENT ON COLUMN "public"."hasn_agents"."api_key_hash" IS 'API Key 的 SHA256 哈希';
COMMENT ON COLUMN "public"."hasn_agents"."capability_summary_json" IS '能力摘要缓存（从 hasn_agent_capabilities 聚合，供 sync/inbox 快速读取）';
COMMENT ON COLUMN "public"."hasn_agents"."capability_revision" IS '能力摘要修订号';
COMMENT ON COLUMN "public"."hasn_agents"."profile_revision" IS 'Agent Profile 修订号';
COMMENT ON COLUMN "public"."hasn_agents"."policy_revision" IS 'Agent 权限/策略修订号';
COMMENT ON COLUMN "public"."hasn_agents"."sync_revision" IS '服务端同步修订号';
COMMENT ON COLUMN "public"."hasn_agents"."runtime_summary_json" IS 'Runtime 脱敏状态摘要缓存；禁止 workspace/endpoint/PID/CLI args/OAuth path';
COMMENT ON COLUMN "public"."hasn_agents"."tags" IS 'Agent 标签数组（云端权威，daemon 仅镜像）';
COMMENT ON COLUMN "public"."hasn_agents"."capability_set_id" IS 'Agent 能力集 ID（与 hasn_agent_capabilities 关联，云端权威）';
COMMENT ON COLUMN "public"."hasn_agents"."persona_ref" IS 'Agent persona 引用（template / persona 资产 ID，云端权威）';
COMMENT ON COLUMN "public"."hasn_agents"."status" IS '状态/生命周期 (active:活跃:green/disabled:已停用:orange/revoked:已吊销:red/archived:已归档:gray/deleted:已删除:gray)';
COMMENT ON COLUMN "public"."hasn_agents"."created_via" IS '创建来源 (guardian:Guardian注册:blue/client:客户端创建:green)';
COMMENT ON COLUMN "public"."hasn_agents"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_agents"."updated_time" IS '更新时间';
