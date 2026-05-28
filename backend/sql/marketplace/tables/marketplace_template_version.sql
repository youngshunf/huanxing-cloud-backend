-- 模板版本表
CREATE TABLE "public"."marketplace_template_version" (
  "id" bigserial PRIMARY KEY,
  "template_id" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "version" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "changelog" text COLLATE "pg_catalog"."default",
  "skill_dependencies_versioned" jsonb,
  "bundle_slug" varchar(100) COLLATE "pg_catalog"."default",
  "command_key" varchar(100) COLLATE "pg_catalog"."default",
  "hermes_bundle_json" jsonb,
  "hermes_yaml" text COLLATE "pg_catalog"."default",
  "content_hash" varchar(128) COLLATE "pg_catalog"."default",
  "package_url" varchar(500) COLLATE "pg_catalog"."default",
  "file_hash" varchar(64) COLLATE "pg_catalog"."default",
  "file_size" int4,
  "is_latest" bool NOT NULL DEFAULT false,
  "published_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("template_id", "version")
);

CREATE INDEX "idx_marketplace_template_version_template_id" ON "public"."marketplace_template_version" ("template_id");
CREATE INDEX "idx_marketplace_template_version_is_latest" ON "public"."marketplace_template_version" ("is_latest");

COMMENT ON COLUMN "public"."marketplace_template_version"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_template_version"."template_id" IS '关联的模板ID';
COMMENT ON COLUMN "public"."marketplace_template_version"."version" IS '语义化版本号';
COMMENT ON COLUMN "public"."marketplace_template_version"."changelog" IS '版本更新日志';
COMMENT ON COLUMN "public"."marketplace_template_version"."skill_dependencies_versioned" IS '带版本号的技能依赖';
COMMENT ON COLUMN "public"."marketplace_template_version"."bundle_slug" IS 'skill pack slug';
COMMENT ON COLUMN "public"."marketplace_template_version"."command_key" IS 'Hermes 命令 key';
COMMENT ON COLUMN "public"."marketplace_template_version"."hermes_bundle_json" IS 'Hermes bundle JSON';
COMMENT ON COLUMN "public"."marketplace_template_version"."hermes_yaml" IS 'Hermes YAML';
COMMENT ON COLUMN "public"."marketplace_template_version"."content_hash" IS '内容哈希';
COMMENT ON COLUMN "public"."marketplace_template_version"."package_url" IS '完整包下载URL';
COMMENT ON COLUMN "public"."marketplace_template_version"."file_hash" IS 'SHA256校验值';
COMMENT ON COLUMN "public"."marketplace_template_version"."file_size" IS '包大小（字节）';
COMMENT ON COLUMN "public"."marketplace_template_version"."is_latest" IS '是否为最新版本';
COMMENT ON COLUMN "public"."marketplace_template_version"."published_at" IS '发布时间';
COMMENT ON TABLE "public"."marketplace_template_version" IS '模板版本表';
