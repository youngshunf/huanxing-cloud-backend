-- 技能市场下载历史表
CREATE TABLE "public"."marketplace_download_history" (
  "id" bigserial PRIMARY KEY,
  "user_id" int8 NOT NULL,
  "resource_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "resource_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "resource_name" varchar(200) COLLATE "pg_catalog"."default",
  "version" varchar(50) COLLATE "pg_catalog"."default",
  "download_source" varchar(50) COLLATE "pg_catalog"."default",
  "ip_address" varchar(50) COLLATE "pg_catalog"."default",
  "user_agent" text COLLATE "pg_catalog"."default",
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW()
);

CREATE INDEX "idx_marketplace_download_history_user_id" ON "public"."marketplace_download_history" ("user_id");
CREATE INDEX "idx_marketplace_download_history_resource_type" ON "public"."marketplace_download_history" ("resource_type");
CREATE INDEX "idx_marketplace_download_history_resource_id" ON "public"."marketplace_download_history" ("resource_id");
CREATE INDEX "idx_marketplace_download_history_created_time" ON "public"."marketplace_download_history" ("created_time" DESC);

COMMENT ON COLUMN "public"."marketplace_download_history"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_download_history"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."marketplace_download_history"."resource_type" IS '资源类型 (skill:技能:blue/template:模板:cyan)';
COMMENT ON COLUMN "public"."marketplace_download_history"."resource_id" IS '资源 ID';
COMMENT ON COLUMN "public"."marketplace_download_history"."resource_name" IS '资源名称';
COMMENT ON COLUMN "public"."marketplace_download_history"."version" IS '版本号';
COMMENT ON COLUMN "public"."marketplace_download_history"."download_source" IS '下载来源（web/api/cli）';
COMMENT ON COLUMN "public"."marketplace_download_history"."ip_address" IS 'IP 地址';
COMMENT ON COLUMN "public"."marketplace_download_history"."user_agent" IS 'User Agent';
COMMENT ON TABLE "public"."marketplace_download_history" IS '技能市场下载历史表';
