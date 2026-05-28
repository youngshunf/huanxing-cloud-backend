-- 用户下载记录表
CREATE TABLE "public"."marketplace_download" (
  "id" bigserial PRIMARY KEY,
  "user_id" int8 NOT NULL,
  "resource_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "resource_id" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "resource_name" varchar(200) COLLATE "pg_catalog"."default",
  "version" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "download_source" varchar(50) COLLATE "pg_catalog"."default",
  "ip_address" varchar(50) COLLATE "pg_catalog"."default",
  "user_agent" text COLLATE "pg_catalog"."default",
  "downloaded_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6)
);

CREATE INDEX "idx_marketplace_download_user_id" ON "public"."marketplace_download" ("user_id");
CREATE INDEX "idx_marketplace_download_resource" ON "public"."marketplace_download" ("resource_type", "resource_id");
CREATE INDEX "idx_marketplace_download_downloaded_at" ON "public"."marketplace_download" ("downloaded_at" DESC);

COMMENT ON COLUMN "public"."marketplace_download"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_download"."user_id" IS '用户ID';
COMMENT ON COLUMN "public"."marketplace_download"."resource_type" IS '资源类型 (skill:技能:blue/template:模板:cyan)';
COMMENT ON COLUMN "public"."marketplace_download"."resource_id" IS '资源 ID';
COMMENT ON COLUMN "public"."marketplace_download"."resource_name" IS '资源名称';
COMMENT ON COLUMN "public"."marketplace_download"."version" IS '下载的版本';
COMMENT ON COLUMN "public"."marketplace_download"."download_source" IS '下载来源（web/api/cli）';
COMMENT ON COLUMN "public"."marketplace_download"."ip_address" IS 'IP 地址';
COMMENT ON COLUMN "public"."marketplace_download"."user_agent" IS 'User Agent';
COMMENT ON COLUMN "public"."marketplace_download"."downloaded_at" IS '下载时间';
COMMENT ON TABLE "public"."marketplace_download" IS '用户下载记录表';
