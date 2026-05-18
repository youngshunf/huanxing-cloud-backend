-- 表 7: app_resources - Resource 定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_resources" (
    -- 主键
    "resource_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 基本信息
    "resource_name" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,

    -- Schema
    "schema_json" JSONB NOT NULL,

    -- 存储策略
    "storage_strategy" VARCHAR(50) NOT NULL DEFAULT 'jsonb',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_resources_resource_id_format" CHECK (
        "resource_id" ~ '^app_[a-z0-9_]+\.[a-z0-9_]+$'
    ),
    CONSTRAINT "chk_app_resources_storage_strategy" CHECK (
        "storage_strategy" IN ('jsonb', 'dedicated_table')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_resources_app_resource_name" ON "public"."app_resources"("app_id", "resource_name");
CREATE INDEX IF NOT EXISTS "idx_app_resources_app_id" ON "public"."app_resources"("app_id");

COMMENT ON TABLE "public"."app_resources" IS 'App Resource 定义表';
COMMENT ON COLUMN "public"."app_resources"."resource_id" IS 'Resource ID';
COMMENT ON COLUMN "public"."app_resources"."storage_strategy" IS '存储策略 (jsonb:JSONB存储:blue/dedicated_table:独立表:green)';

-- ============================================================================
