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

-- 5. 如果 marketplace_download_history 表存在数据，迁移到 marketplace_download
-- 注意：这里假设 marketplace_download_history 的 resource_type/resource_id 对应 marketplace_download 的字段
INSERT INTO "public"."marketplace_download" (
  "user_id",
  "resource_type",
  "resource_id",
  "resource_name",
  "version",
  "download_source",
  "ip_address",
  "user_agent",
  "downloaded_at",
  "created_time"
)
SELECT
  "user_id",
  "resource_type",
  "resource_id",
  "resource_name",
  "version",
  "download_source",
  "ip_address",
  "user_agent",
  "created_time" as "downloaded_at",
  "created_time"
FROM "public"."marketplace_download_history"
WHERE NOT EXISTS (
  SELECT 1 FROM "public"."marketplace_download" md
  WHERE md."user_id" = "marketplace_download_history"."user_id"
    AND md."resource_type" = "marketplace_download_history"."resource_type"
    AND md."resource_id" = "marketplace_download_history"."resource_id"
    AND md."version" = "marketplace_download_history"."version"
    AND md."downloaded_at" = "marketplace_download_history"."created_time"
);

-- 6. 删除 marketplace_download_history 表
DROP TABLE IF EXISTS "public"."marketplace_download_history";

COMMIT;
