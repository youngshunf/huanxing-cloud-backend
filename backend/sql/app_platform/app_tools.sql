-- 表 6: app_tools - Tool 定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_tools" (
    -- 主键
    "tool_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 基本信息
    "tool_name" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,

    -- Schema
    "input_schema" JSONB NOT NULL,
    "output_schema" JSONB NOT NULL,

    -- 可见性
    "visibility" VARCHAR(50) NOT NULL DEFAULT 'private',

    -- 风险等级
    "risk_level" VARCHAR(50) NOT NULL DEFAULT 'low',

    -- 所需权限
    "required_scopes" JSONB NOT NULL DEFAULT '[]',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_tools_tool_id_format" CHECK (
        "tool_id" ~ '^app_[a-z0-9_]+\.[a-z0-9_]+$'
    ),
    CONSTRAINT "chk_app_tools_visibility" CHECK (
        "visibility" IN ('private', 'public_service')
    ),
    CONSTRAINT "chk_app_tools_risk_level" CHECK (
        "risk_level" IN ('low', 'medium', 'high')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_tools_app_tool_name" ON "public"."app_tools"("app_id", "tool_name");
CREATE INDEX IF NOT EXISTS "idx_app_tools_app_id" ON "public"."app_tools"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_tools_visibility" ON "public"."app_tools"("visibility");

COMMENT ON TABLE "public"."app_tools" IS 'App Tool 定义表';
COMMENT ON COLUMN "public"."app_tools"."tool_id" IS 'Tool ID';
COMMENT ON COLUMN "public"."app_tools"."visibility" IS '可见性 (private:私有:gray/public_service:公开服务:green)';
COMMENT ON COLUMN "public"."app_tools"."risk_level" IS '风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)';

-- ============================================================================
