-- 表 2: app_manifests - App 清单表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_manifests" (
    -- 主键
    "app_id" VARCHAR(255) PRIMARY KEY,

    -- 基本信息
    "developer_id" UUID NOT NULL,
    "namespace" VARCHAR(100) NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "icon_url" VARCHAR(500),

    -- 版本信息
    "current_version" VARCHAR(50) NOT NULL,

    -- 运行模式
    "backend_runtime_mode" VARCHAR(50) NOT NULL DEFAULT 'platform_hosted',
    "frontend_hosting_mode" VARCHAR(50) NOT NULL DEFAULT 'none',

    -- 权限声明
    "requested_scopes" JSONB NOT NULL DEFAULT '[]',

    -- 分类
    "category" VARCHAR(100),
    "tags" JSONB DEFAULT '[]',

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'draft',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_manifests_app_id_format" CHECK (
        "app_id" ~ '^app_[a-z0-9_]+$'
    ),
    CONSTRAINT "chk_app_manifests_backend_runtime_mode" CHECK (
        "backend_runtime_mode" IN ('platform_hosted', 'external_hosted')
    ),
    CONSTRAINT "chk_app_manifests_frontend_hosting_mode" CHECK (
        "frontend_hosting_mode" IN ('none', 'platform_hosted', 'external_hosted')
    ),
    CONSTRAINT "chk_app_manifests_status" CHECK (
        "status" IN ('draft', 'submitted', 'approved', 'rejected', 'published', 'archived')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_manifests_namespace_name" ON "public"."app_manifests"("namespace", "name");
CREATE INDEX IF NOT EXISTS "idx_app_manifests_developer_id" ON "public"."app_manifests"("developer_id");
CREATE INDEX IF NOT EXISTS "idx_app_manifests_status" ON "public"."app_manifests"("status");

COMMENT ON TABLE "public"."app_manifests" IS 'App 清单表';
COMMENT ON COLUMN "public"."app_manifests"."app_id" IS 'App ID';
COMMENT ON COLUMN "public"."app_manifests"."developer_id" IS '开发者 ID';
COMMENT ON COLUMN "public"."app_manifests"."display_name" IS '显示名称';
COMMENT ON COLUMN "public"."app_manifests"."backend_runtime_mode" IS '后端运行模式 (platform_hosted:平台托管:blue/external_hosted:外部托管:green)';
COMMENT ON COLUMN "public"."app_manifests"."frontend_hosting_mode" IS '前端托管模式 (none:无前端:gray/platform_hosted:平台托管:blue/external_hosted:外部托管:green)';
COMMENT ON COLUMN "public"."app_manifests"."status" IS '状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/archived:已归档:gray)';

-- ============================================================================
