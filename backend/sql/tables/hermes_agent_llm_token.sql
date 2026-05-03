CREATE TABLE "public"."hermes_agent_llm_token" (
  "id" bigserial PRIMARY KEY,
  "agent_id" varchar(64) NOT NULL,
  "user_id" int8 NOT NULL,
  "newapi_user_id" int8 NOT NULL,
  "newapi_token_id" int8 NOT NULL,
  "token_key_prefix" varchar(16) NOT NULL,
  "token_key_sha256" varchar(64) NOT NULL,
  "model_allowlist" jsonb,
  "rate_limit_rps" int4,
  "per_token_quota_remaining" int8,
  "issued_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "revoked_at" timestamptz(6),
  "runtime_node_id" varchar(64),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE ("agent_id"),
  UNIQUE ("newapi_token_id")
);

CREATE INDEX "idx_hermes_agent_llm_token_user_id" ON "public"."hermes_agent_llm_token" ("user_id");
CREATE INDEX "idx_hermes_agent_llm_token_agent_id" ON "public"."hermes_agent_llm_token" ("agent_id");
CREATE INDEX "idx_hermes_agent_llm_token_newapi_token_id" ON "public"."hermes_agent_llm_token" ("newapi_token_id");

COMMENT ON TABLE "public"."hermes_agent_llm_token" IS 'Hermes Agent 级 LLM token 隔离记录';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."agent_id" IS 'Agent 业务 ID';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."user_id" IS '唤星用户 ID';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."newapi_user_id" IS 'new-api users.id';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."newapi_token_id" IS 'new-api tokens.id';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."token_key_prefix" IS 'token 明文前 8 字符（脱敏展示与审计）';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."token_key_sha256" IS 'token 明文 SHA256（反查匹配，不可逆）';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."model_allowlist" IS '平台模型白名单 JSON，留空 = 跟随 user 默认';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."rate_limit_rps" IS '单 Agent QPS 限速，留空 = 跟随 user 默认';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."per_token_quota_remaining" IS '可选：单 token 独立配额；留空 = 与 user.quota 共享';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."issued_at" IS '签发时间';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."revoked_at" IS '撤销时间，NULL 表示有效';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."runtime_node_id" IS 'Runtime 节点 ID（预留 §08）';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hermes_agent_llm_token"."updated_time" IS '更新时间';
