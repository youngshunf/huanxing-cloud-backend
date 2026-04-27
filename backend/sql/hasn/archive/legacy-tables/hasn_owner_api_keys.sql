-- HASN Owner API Key 表
CREATE TABLE "public"."hasn_owner_api_keys" (
  "id"             bigserial PRIMARY KEY,
  "key_id"         varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id"        bigint,
  "owner_id"       varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "key_name"       varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "key_hash"       varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "status"         varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'active',
  "scopes"         jsonb NOT NULL DEFAULT '[]',
  "bound_node_id"  varchar(40) COLLATE "pg_catalog"."default",
  "expires_at"     timestamptz(6),
  "last_used_at"   timestamptz(6),
  "revoked_at"     timestamptz(6),
  "revoke_reason"  varchar(50) COLLATE "pg_catalog"."default",
  "created_time"   timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time"   timestamptz(6),
  UNIQUE("key_id")
);

CREATE INDEX "idx_hasn_owner_api_keys_user" ON "public"."hasn_owner_api_keys" ("user_id");
CREATE INDEX "idx_hasn_owner_api_keys_owner" ON "public"."hasn_owner_api_keys" ("owner_id");
CREATE INDEX "idx_hasn_owner_api_keys_status" ON "public"."hasn_owner_api_keys" ("status");
CREATE INDEX "idx_hasn_owner_api_keys_bound_node" ON "public"."hasn_owner_api_keys" ("bound_node_id");

COMMENT ON TABLE "public"."hasn_owner_api_keys" IS 'HASN Owner API Key 表';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."key_id" IS 'Owner API Key 唯一标识';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."user_id" IS '平台用户 ID（桌面端/唤星账号场景）';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."owner_id" IS 'Owner 的 hasn_id (格式: h_xxx)';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."key_name" IS 'Key 名称';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."key_hash" IS 'Owner API Key 的 SHA256 哈希';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."status" IS '状态 (active:生效中:green/revoked:已吊销:red/deleted:已删除:gray)';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."scopes" IS '授权 scopes JSON';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."bound_node_id" IS '绑定 Node ID（可为空）';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."expires_at" IS '过期时间';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."last_used_at" IS '最后使用时间';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."revoked_at" IS '吊销时间';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."revoke_reason" IS '吊销原因 (manual_revoke:手动吊销:orange/credential_rotated:凭据轮换:blue/policy_violation:策略违规:red)';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_owner_api_keys"."updated_time" IS '更新时间';
