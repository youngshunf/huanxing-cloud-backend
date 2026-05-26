-- 第三方应用集成配置表
CREATE TABLE "public"."integration_apps" (
  "id" bigserial PRIMARY KEY,
  "app_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "app_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "app_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "base_url" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "config" jsonb,
  "is_enabled" bool NOT NULL DEFAULT true,
  "description" text COLLATE "pg_catalog"."default",
  "icon_url" varchar(500) COLLATE "pg_catalog"."default",
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("app_id")
);

CREATE INDEX "idx_integration_apps_app_type" ON "public"."integration_apps" ("app_type");
CREATE INDEX "idx_integration_apps_is_enabled" ON "public"."integration_apps" ("is_enabled");

COMMENT ON COLUMN "public"."integration_apps"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."integration_apps"."app_id" IS '应用唯一标识（如 clawhub）';
COMMENT ON COLUMN "public"."integration_apps"."app_name" IS '应用名称（如 ClawHub 技能市场）';
COMMENT ON COLUMN "public"."integration_apps"."app_type" IS '应用类型（用于实例化对应的集成类，如 clawhub/github/feishu）';
COMMENT ON COLUMN "public"."integration_apps"."base_url" IS '应用基础 URL';
COMMENT ON COLUMN "public"."integration_apps"."config" IS '应用配置（JSON 格式，包含 API 端点、超时设置等）';
COMMENT ON COLUMN "public"."integration_apps"."is_enabled" IS '是否启用';
COMMENT ON COLUMN "public"."integration_apps"."description" IS '应用描述';
COMMENT ON COLUMN "public"."integration_apps"."icon_url" IS '应用图标 URL';
COMMENT ON TABLE "public"."integration_apps" IS '第三方应用集成配置表';
