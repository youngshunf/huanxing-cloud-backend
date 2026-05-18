-- 表 8: app_events - Event 定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_events" (
    -- 主键
    "event_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 基本信息
    "event_type" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,

    -- Schema
    "payload_schema" JSONB NOT NULL,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_events_event_id_format" CHECK (
        "event_id" ~ '^app_[a-z0-9_]+\.[a-z0-9_]+$'
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_events_app_event_type" ON "public"."app_events"("app_id", "event_type");
CREATE INDEX IF NOT EXISTS "idx_app_events_app_id" ON "public"."app_events"("app_id");

COMMENT ON TABLE "public"."app_events" IS 'App Event 定义表';
COMMENT ON COLUMN "public"."app_events"."event_id" IS 'Event ID';

-- ============================================================================
