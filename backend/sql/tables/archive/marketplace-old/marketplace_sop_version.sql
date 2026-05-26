-- SOP 工作流版本表
CREATE TABLE "public"."marketplace_sop_version" (
  "id" bigserial PRIMARY KEY,
  "sop_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "version" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "changelog" text COLLATE "pg_catalog"."default",
  "package_url" varchar(500) COLLATE "pg_catalog"."default",
  "file_hash" varchar(64) COLLATE "pg_catalog"."default",
  "file_size" int4,
  "is_latest" bool NOT NULL DEFAULT false,
  "published_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("sop_id", "version")
);

CREATE INDEX "idx_marketplace_sop_version_sop_id" ON "public"."marketplace_sop_version" ("sop_id");
CREATE INDEX "idx_marketplace_sop_version_is_latest" ON "public"."marketplace_sop_version" ("is_latest");

COMMENT ON COLUMN "public"."marketplace_sop_version"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_sop_version"."sop_id" IS '关联的SOP ID';
COMMENT ON COLUMN "public"."marketplace_sop_version"."version" IS '语义化版本号';
COMMENT ON COLUMN "public"."marketplace_sop_version"."changelog" IS '版本更新日志';
COMMENT ON COLUMN "public"."marketplace_sop_version"."package_url" IS '完整包下载URL';
COMMENT ON COLUMN "public"."marketplace_sop_version"."file_hash" IS 'SHA256校验值';
COMMENT ON COLUMN "public"."marketplace_sop_version"."file_size" IS '包大小（字节）';
COMMENT ON COLUMN "public"."marketplace_sop_version"."is_latest" IS '是否为最新版本';
COMMENT ON COLUMN "public"."marketplace_sop_version"."published_at" IS '发布时间';
COMMENT ON TABLE "public"."marketplace_sop_version" IS 'SOP工作流版本表';
