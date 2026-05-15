-- ============================================================================
-- 表 2: app_scopes - 应用权限定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_scopes" (
    -- 主键
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,

    -- 权限信息
    "scope" VARCHAR(255) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "reason" TEXT,

    -- 风险等级
    "risk_level" VARCHAR(20) NOT NULL,

    -- 权限控制
    "requires_owner_confirmation" BOOLEAN DEFAULT FALSE,

    -- 限流配置
    "rate_limit_per_minute" INTEGER,
    "rate_limit_per_hour" INTEGER,
    "rate_limit_per_day" INTEGER,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_scopes_scope_format" CHECK (
        "scope" ~ '^[a-z0-9_]+\.[a-z_]+\.[a-z_]+$'
    ),
    CONSTRAINT "chk_app_scopes_risk_level" CHECK (
        "risk_level" IN ('low', 'medium', 'high')
    )
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_scopes_app_scope" ON "public"."app_scopes"("app_id", "scope");
CREATE INDEX IF NOT EXISTS "idx_app_scopes_app_id" ON "public"."app_scopes"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_scopes_risk_level" ON "public"."app_scopes"("risk_level");

-- 表注释
COMMENT ON TABLE "public"."app_scopes" IS '应用权限定义表';

-- 字段注释
COMMENT ON COLUMN "public"."app_scopes"."id" IS '主键 UUID';
COMMENT ON COLUMN "public"."app_scopes"."app_id" IS '关联的 App ID';
COMMENT ON COLUMN "public"."app_scopes"."scope" IS '权限标识';
COMMENT ON COLUMN "public"."app_scopes"."display_name" IS '权限显示名称';
COMMENT ON COLUMN "public"."app_scopes"."description" IS '权限描述';
COMMENT ON COLUMN "public"."app_scopes"."reason" IS '为什么需要这个权限';
COMMENT ON COLUMN "public"."app_scopes"."risk_level" IS '风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)';
COMMENT ON COLUMN "public"."app_scopes"."requires_owner_confirmation" IS '是否需要 Owner 二次确认';
COMMENT ON COLUMN "public"."app_scopes"."rate_limit_per_minute" IS '每分钟限流次数';
COMMENT ON COLUMN "public"."app_scopes"."rate_limit_per_hour" IS '每小时限流次数';
COMMENT ON COLUMN "public"."app_scopes"."rate_limit_per_day" IS '每天限流次数';
COMMENT ON COLUMN "public"."app_scopes"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."app_scopes"."updated_time" IS '更新时间';
