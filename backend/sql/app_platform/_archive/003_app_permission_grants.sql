-- ============================================================================
-- 表 3: app_permission_grants - 权限授予记录表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_permission_grants" (
    -- 主键
    "grant_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "installation_id" VARCHAR(255) NOT NULL,
    "scope" VARCHAR(255) NOT NULL,

    -- 授予信息
    "granted_by" VARCHAR(255) NOT NULL,
    "granted_at" TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "grant_source" VARCHAR(50) NOT NULL,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 撤销信息
    "revoked_at" TIMESTAMP,
    "revoked_by" VARCHAR(255),
    "revocation_reason" TEXT,

    -- 使用统计
    "last_used_at" TIMESTAMP,
    "usage_count" INTEGER NOT NULL DEFAULT 0,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_permission_grants_grant_source" CHECK (
        "grant_source" IN ('installation', 'dynamic_request', 'version_upgrade')
    ),
    CONSTRAINT "chk_app_permission_grants_status" CHECK (
        "status" IN ('active', 'revoked')
    )
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_permission_grants_installation_scope"
    ON "public"."app_permission_grants"("installation_id", "scope")
    WHERE "status" = 'active';
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_installation_id" ON "public"."app_permission_grants"("installation_id");
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_scope" ON "public"."app_permission_grants"("scope");
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_status" ON "public"."app_permission_grants"("status");
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_granted_at" ON "public"."app_permission_grants"("granted_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_last_used_at" ON "public"."app_permission_grants"("last_used_at" DESC NULLS LAST);

-- 表注释
COMMENT ON TABLE "public"."app_permission_grants" IS '权限授予记录表';

-- 字段注释
COMMENT ON COLUMN "public"."app_permission_grants"."grant_id" IS '授权记录 ID';
COMMENT ON COLUMN "public"."app_permission_grants"."installation_id" IS '关联的 Installation ID';
COMMENT ON COLUMN "public"."app_permission_grants"."scope" IS '授予的权限标识';
COMMENT ON COLUMN "public"."app_permission_grants"."granted_by" IS '授予者 Owner ID';
COMMENT ON COLUMN "public"."app_permission_grants"."granted_at" IS '授予时间';
COMMENT ON COLUMN "public"."app_permission_grants"."grant_source" IS '授予来源 (installation:安装时:blue/dynamic_request:动态请求:green/version_upgrade:版本升级:orange)';
COMMENT ON COLUMN "public"."app_permission_grants"."status" IS '状态 (active:生效:green/revoked:已撤销:red)';
COMMENT ON COLUMN "public"."app_permission_grants"."revoked_at" IS '撤销时间';
COMMENT ON COLUMN "public"."app_permission_grants"."revoked_by" IS '撤销者';
COMMENT ON COLUMN "public"."app_permission_grants"."revocation_reason" IS '撤销原因';
COMMENT ON COLUMN "public"."app_permission_grants"."last_used_at" IS '最后使用时间';
COMMENT ON COLUMN "public"."app_permission_grants"."usage_count" IS '使用次数';
COMMENT ON COLUMN "public"."app_permission_grants"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."app_permission_grants"."updated_time" IS '更新时间';
