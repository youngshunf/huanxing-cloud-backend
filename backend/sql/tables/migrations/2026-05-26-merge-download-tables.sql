-- 合并 marketplace_download 和 marketplace_download_history 表
-- 保留 marketplace_download，添加 marketplace_download_history 的额外字段

BEGIN;

-- 1. 为 marketplace_download 添加新字段
ALTER TABLE "public"."marketplace_download"
  ADD COLUMN IF NOT EXISTS "resource_name" varchar(200) COLLATE "pg_catalog"."default",
  ADD COLUMN IF NOT EXISTS "download_source" varchar(50) COLLATE "pg_catalog"."default",
  ADD COLUMN IF NOT EXISTS "ip_address" varchar(50) COLLATE "pg_catalog"."default",
  ADD COLUMN IF NOT EXISTS "user_agent" text COLLATE "pg_catalog"."default";

-- 2. 重命名字段以统一命名规范
ALTER TABLE "public"."marketplace_download"
  RENAME COLUMN "item_type" TO "resource_type";

ALTER TABLE "public"."marketplace_download"
  RENAME COLUMN "item_id" TO "resource_id";

-- 3. 更新索引
DROP INDEX IF EXISTS "idx_marketplace_download_item";
CREATE INDEX "idx_marketplace_download_resource" ON "public"."marketplace_download" ("resource_type", "resource_id");

-- 4. 更新字段注释
COMMENT ON COLUMN "public"."marketplace_download"."resource_type" IS '资源类型 (skill:技能:blue/template:模板:cyan)';
COMMENT ON COLUMN "public"."marketplace_download"."resource_id" IS '资源 ID';
COMMENT ON COLUMN "public"."marketplace_download"."resource_name" IS '资源名称';
COMMENT ON COLUMN "public"."marketplace_download"."download_source" IS '下载来源（web/api/cli）';
COMMENT ON COLUMN "public"."marketplace_download"."ip_address" IS 'IP 地址';
COMMENT ON COLUMN "public"."marketplace_download"."user_agent" IS 'User Agent';



COMMIT;
