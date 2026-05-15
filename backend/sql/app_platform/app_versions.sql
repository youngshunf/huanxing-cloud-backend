-- 表 3: app_versions - App 版本表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_versions" (
    -- 主键
    "version_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version" VARCHAR(50) NOT NULL,

    -- 版本信息
    "changelog" TEXT,
    "manifest_snapshot" JSONB NOT NULL,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'draft',

    -- 发布信息
    "published_at" TIMESTAMP,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_versions_status" CHECK (
        "status" IN ('draft', 'submitted', 'approved', 'rejected', 'published', 'deprecated')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_versions_app_version" ON "public"."app_versions"("app_id", "version");
CREATE INDEX IF NOT EXISTS "idx_app_versions_app_id" ON "public"."app_versions"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_versions_status" ON "public"."app_versions"("status");

COMMENT ON TABLE "public"."app_versions" IS 'App 版本表';
COMMENT ON COLUMN "public"."app_versions"."version_id" IS '版本 ID';
COMMENT ON COLUMN "public"."app_versions"."app_id" IS 'App ID';
COMMENT ON COLUMN "public"."app_versions"."version" IS '版本号';
COMMENT ON COLUMN "public"."app_versions"."manifest_snapshot" IS 'Manifest 快照（JSONB）';
COMMENT ON COLUMN "public"."app_versions"."status" IS '状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/deprecated:已废弃:orange)';

-- ============================================================================
