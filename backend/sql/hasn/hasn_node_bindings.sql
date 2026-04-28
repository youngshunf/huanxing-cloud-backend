-- =====================================================
-- HASN Node Owner Binding 租约表（S0/S1 codegen 输入）
-- =====================================================
CREATE TABLE "public"."hasn_node_bindings" (
  "id"            bigserial PRIMARY KEY,
  "binding_id"    varchar(40) NOT NULL,
  "node_id"       varchar(40) NOT NULL,
  "owner_id"      varchar(40) NOT NULL,
  "auth_profile"  varchar(30) NOT NULL DEFAULT 'bearer_token',
  "scopes"        jsonb NOT NULL DEFAULT '{}',
  "status"        varchar(20) NOT NULL DEFAULT 'active',
  "bound_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at"    timestamptz(6) NOT NULL,
  "renewed_at"    timestamptz(6),
  "revoked_at"    timestamptz(6),
  "revoke_reason" varchar(50),
  "last_used_at"  timestamptz(6),
  "sync_revision" bigint NOT NULL DEFAULT 1,
  "created_time"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"  timestamptz(6),
  CONSTRAINT "uq_hasn_node_bindings_binding" UNIQUE ("binding_id")
);

CREATE INDEX "idx_hasn_node_bindings_node" ON "public"."hasn_node_bindings" ("node_id");
CREATE INDEX "idx_hasn_node_bindings_owner" ON "public"."hasn_node_bindings" ("owner_id");
CREATE INDEX "idx_hasn_node_bindings_status" ON "public"."hasn_node_bindings" ("status");
CREATE INDEX "idx_hasn_node_bindings_expires" ON "public"."hasn_node_bindings" ("expires_at");
CREATE INDEX "idx_hasn_node_bindings_sync_revision" ON "public"."hasn_node_bindings" ("sync_revision");

COMMENT ON TABLE "public"."hasn_node_bindings" IS 'HASN Node Owner Binding 租约表';
COMMENT ON COLUMN "public"."hasn_node_bindings"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_node_bindings"."binding_id" IS '绑定唯一标识 (格式: ob_{uuid})';
COMMENT ON COLUMN "public"."hasn_node_bindings"."node_id" IS '节点 ID (格式: n_{uuid_short})';
COMMENT ON COLUMN "public"."hasn_node_bindings"."owner_id" IS 'Owner 的 hasn_id (格式: h_xxx)';
COMMENT ON COLUMN "public"."hasn_node_bindings"."auth_profile" IS '认证模式 (bearer_token:平台令牌:blue/owner_api_key:Owner API Key:green/mtls_bound_token:mTLS绑定令牌:purple/dpop_token:DPoP令牌:cyan)';
COMMENT ON COLUMN "public"."hasn_node_bindings"."scopes" IS '授权 scopes JSON';
COMMENT ON COLUMN "public"."hasn_node_bindings"."status" IS '状态 (active:生效中:green/expired:已过期:orange/revoked:已吊销:red/removed:已解绑:gray)';
COMMENT ON COLUMN "public"."hasn_node_bindings"."bound_at" IS '绑定时间';
COMMENT ON COLUMN "public"."hasn_node_bindings"."expires_at" IS '过期时间';
COMMENT ON COLUMN "public"."hasn_node_bindings"."renewed_at" IS '最近续期时间';
COMMENT ON COLUMN "public"."hasn_node_bindings"."revoked_at" IS '吊销时间';
COMMENT ON COLUMN "public"."hasn_node_bindings"."revoke_reason" IS '吊销原因 (manual_revoke:手动吊销:orange/credential_rotated:凭据轮换:blue/policy_violation:策略违规:red)';
COMMENT ON COLUMN "public"."hasn_node_bindings"."last_used_at" IS '最后使用时间';
COMMENT ON COLUMN "public"."hasn_node_bindings"."sync_revision" IS '服务端同步修订号';
COMMENT ON COLUMN "public"."hasn_node_bindings"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_node_bindings"."updated_time" IS '更新时间';
