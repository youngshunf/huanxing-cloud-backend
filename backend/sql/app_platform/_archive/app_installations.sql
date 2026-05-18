-- 表 5: app_installations - 安装记录表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_installations" (
    -- 主键
    "installation_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "owner_id" VARCHAR(255) NOT NULL,
    "app_id" VARCHAR(255) NOT NULL,
    "listing_id" UUID NOT NULL,

    -- 版本信息
    "installed_version" VARCHAR(50) NOT NULL,

    -- 权限
    "granted_scopes" JSONB NOT NULL DEFAULT '[]',

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 安装信息
    "installed_at" TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_used_at" TIMESTAMP,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_installations_installation_id_format" CHECK (
        "installation_id" ~ '^appi_[a-z0-9_-]+$'
    ),
    CONSTRAINT "chk_app_installations_status" CHECK (
        "status" IN ('active', 'update_available', 'pending_reauth', 'suspended', 'revoked')
    )
);

CREATE INDEX IF NOT EXISTS "idx_app_installations_owner_id" ON "public"."app_installations"("owner_id");
CREATE INDEX IF NOT EXISTS "idx_app_installations_app_id" ON "public"."app_installations"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_installations_status" ON "public"."app_installations"("status");

COMMENT ON TABLE "public"."app_installations" IS 'App 安装记录表';
COMMENT ON COLUMN "public"."app_installations"."installation_id" IS 'Installation ID';
COMMENT ON COLUMN "public"."app_installations"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."app_installations"."granted_scopes" IS '授予的权限列表（JSONB）';
COMMENT ON COLUMN "public"."app_installations"."status" IS '状态 (active:活跃:green/update_available:有更新:blue/pending_reauth:待重新授权:orange/suspended:已暂停:red/revoked:已撤销:red)';

-- ============================================================================
