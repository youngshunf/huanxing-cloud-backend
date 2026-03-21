-- HASN Agent 表（全新设计，替代旧表）
-- 注意：依赖 hasn_clients 表（home_client_id 外键），必须先建 hasn_clients
CREATE TABLE "public"."hasn_agents" (
  "id"             bigserial PRIMARY KEY,
  "hasn_id"        varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "star_id"        varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "owner_id"       varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "name"           varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "agent_name"     varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "type"           varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'cloud',
  "server_id"      varchar(50) COLLATE "pg_catalog"."default",
  "home_client_id" int8,
  "api_key_hash"   varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "status"         varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'active',
  "created_via"    varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'guardian',
  "created_time"   timestamptz(6) NOT NULL DEFAULT NOW(),
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

COMMENT ON TABLE "public"."hasn_agents" IS 'HASN Agent 表';
COMMENT ON COLUMN "public"."hasn_agents"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_agents"."hasn_id" IS 'HASN Agent 唯一标识 (格式: a_{uuid})';
COMMENT ON COLUMN "public"."hasn_agents"."star_id" IS 'Agent 唤星号 (如: 100001#star)';
COMMENT ON COLUMN "public"."hasn_agents"."owner_id" IS '所属 Human 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_agents"."name" IS 'Agent 显示名';
COMMENT ON COLUMN "public"."hasn_agents"."agent_name" IS 'Agent 标识名';
COMMENT ON COLUMN "public"."hasn_agents"."type" IS 'Agent 类型 (cloud:云端:blue/local:本地:green)';
COMMENT ON COLUMN "public"."hasn_agents"."server_id" IS '云端 Agent 所在服务器 ID';
COMMENT ON COLUMN "public"."hasn_agents"."home_client_id" IS '本地 Agent 归属客户端 ID';
COMMENT ON COLUMN "public"."hasn_agents"."api_key_hash" IS 'API Key 的 SHA256 哈希';
COMMENT ON COLUMN "public"."hasn_agents"."status" IS '状态 (active:活跃:green/disabled:已停用:orange/revoked:已吊销:red)';
COMMENT ON COLUMN "public"."hasn_agents"."created_via" IS '创建来源 (guardian:Guardian注册:blue/client:客户端创建:green)';
COMMENT ON COLUMN "public"."hasn_agents"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_agents"."updated_time" IS '更新时间';
