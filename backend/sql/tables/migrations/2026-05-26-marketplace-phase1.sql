-- =====================================================
-- 2026-05-26 技能市场 Phase 1 数据库迁移
-- 目标:
--   1. 重命名 marketplace_app 表为 marketplace_template
--   2. 为 marketplace_skill 添加 namespace 相关字段
--   3. 为 marketplace_template 添加多语言字段
--   4. 创建 marketplace_sync_log 表
--   5. 创建 marketplace_download_history 表
-- =====================================================

-- ============================================================
-- 1. 重命名 marketplace_app 表为 marketplace_template
-- ============================================================

-- 重命名表
ALTER TABLE IF EXISTS "public"."marketplace_app"
  RENAME TO "marketplace_template";

-- 重命名表注释
COMMENT ON TABLE "public"."marketplace_template" IS '技能市场模板表（Agent模板/技能包/SOP包）';

-- 重命名 app_id 列为 template_id
ALTER TABLE IF EXISTS "public"."marketplace_template"
  RENAME COLUMN "app_id" TO "template_id";

COMMENT ON COLUMN "public"."marketplace_template"."template_id" IS '模板唯一标识';

-- 重命名 app_type 列为 template_type
ALTER TABLE IF EXISTS "public"."marketplace_template"
  RENAME COLUMN "app_type" TO "template_type";

COMMENT ON COLUMN "public"."marketplace_template"."template_type" IS '模板类型 (agent_template:Agent模板:blue/skill_pack:技能包:cyan/sop_pack:SOP包:purple)';

-- 重命名索引
ALTER INDEX IF EXISTS "idx_marketplace_app_author_id"
  RENAME TO "idx_marketplace_template_author_id";

ALTER INDEX IF EXISTS "idx_marketplace_app_pricing_type"
  RENAME TO "idx_marketplace_template_pricing_type";

ALTER INDEX IF EXISTS "idx_marketplace_app_download_count"
  RENAME TO "idx_marketplace_template_download_count";

ALTER INDEX IF EXISTS "idx_marketplace_app_app_type"
  RENAME TO "idx_marketplace_template_template_type";

-- 重命名唯一约束
ALTER TABLE "public"."marketplace_template"
  DROP CONSTRAINT IF EXISTS "marketplace_app_app_id_key";

ALTER TABLE "public"."marketplace_template"
  ADD CONSTRAINT "marketplace_template_template_id_key" UNIQUE ("template_id");

-- ============================================================
-- 2. 为 marketplace_skill 添加 namespace 相关字段
-- ============================================================

-- 添加 namespace 字段（命名空间，如 huanxing/clawhub）
ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "namespace" varchar(50) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."namespace" IS '命名空间（如 huanxing/clawhub）';

-- 添加 slug 字段（技能标识符，如 translator-pro）
ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "slug" varchar(100) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."slug" IS '技能标识符（如 translator-pro）';

-- 添加 source_type 字段（来源类型）
ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "source_type" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'github';

COMMENT ON COLUMN "public"."marketplace_skill"."source_type" IS '来源类型 (github:GitHub:blue/clawhub:ClawHub:green/local:本地:gray)';

-- 添加 source_repo_url 字段（源仓库 URL）
ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "source_repo_url" varchar(500) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."source_repo_url" IS '源仓库 URL';

-- 添加 source_repo_path 字段（仓库内路径）
ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "source_repo_path" varchar(500) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."source_repo_path" IS '仓库内路径（如 skills/translator-pro）';

-- 添加多语言字段
ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "name_en" varchar(200) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."name_en" IS '英文名称';

ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "name_zh" varchar(200) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."name_zh" IS '中文名称';

ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "description_en" text COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."description_en" IS '英文描述';

ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "description_zh" text COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."description_zh" IS '中文描述';

ALTER TABLE "public"."marketplace_skill"
  ADD COLUMN IF NOT EXISTS "source_language" varchar(10) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_skill"."source_language" IS '源语言（en/zh，用于判断哪个是原文）';

-- 创建 namespace + slug 的唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS "idx_marketplace_skill_namespace_slug"
  ON "public"."marketplace_skill" ("namespace", "slug");

-- 创建 source_type 索引
CREATE INDEX IF NOT EXISTS "idx_marketplace_skill_source_type"
  ON "public"."marketplace_skill" ("source_type");

-- ============================================================
-- 3. 为 marketplace_template 添加多语言字段
-- ============================================================

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "name_en" varchar(200) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."name_en" IS '英文名称';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "name_zh" varchar(200) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."name_zh" IS '中文名称';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "description_en" text COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."description_en" IS '英文描述';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "description_zh" text COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."description_zh" IS '中文描述';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "source_language" varchar(10) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."source_language" IS '源语言（en/zh，用于判断哪个是原文）';

-- 添加 namespace 相关字段
ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "namespace" varchar(50) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."namespace" IS '命名空间（如 huanxing/clawhub）';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "slug" varchar(100) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."slug" IS '模板标识符';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "source_type" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'github';

COMMENT ON COLUMN "public"."marketplace_template"."source_type" IS '来源类型 (github:GitHub:blue/clawhub:ClawHub:green/local:本地:gray)';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "source_repo_url" varchar(500) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."source_repo_url" IS '源仓库 URL';

ALTER TABLE "public"."marketplace_template"
  ADD COLUMN IF NOT EXISTS "source_repo_path" varchar(500) COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "public"."marketplace_template"."source_repo_path" IS '仓库内路径';

-- 创建 namespace + slug 的唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS "idx_marketplace_template_namespace_slug"
  ON "public"."marketplace_template" ("namespace", "slug");

-- ============================================================
-- 4. 创建 marketplace_sync_log 表
-- ============================================================

CREATE TABLE IF NOT EXISTS "public"."marketplace_sync_log" (
  "id" bigserial PRIMARY KEY,
  "sync_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "source" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'running',
  "total_count" int4 NOT NULL DEFAULT 0,
  "success_count" int4 NOT NULL DEFAULT 0,
  "failed_count" int4 NOT NULL DEFAULT 0,
  "error_message" text COLLATE "pg_catalog"."default",
  "started_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "completed_at" timestamptz(6),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6)
);

CREATE INDEX "idx_marketplace_sync_log_sync_type" ON "public"."marketplace_sync_log" ("sync_type");
CREATE INDEX "idx_marketplace_sync_log_source" ON "public"."marketplace_sync_log" ("source");
CREATE INDEX "idx_marketplace_sync_log_status" ON "public"."marketplace_sync_log" ("status");
CREATE INDEX "idx_marketplace_sync_log_started_at" ON "public"."marketplace_sync_log" ("started_at" DESC);

COMMENT ON COLUMN "public"."marketplace_sync_log"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_sync_log"."sync_type" IS '同步类型 (skill:技能:blue/template:模板:cyan/full:全量:purple)';
COMMENT ON COLUMN "public"."marketplace_sync_log"."source" IS '同步来源 (github:GitHub:blue/clawhub:ClawHub:green/webhook:Webhook:purple/manual:手动:gray)';
COMMENT ON COLUMN "public"."marketplace_sync_log"."status" IS '同步状态 (running:运行中:blue/success:成功:green/failed:失败:red/partial:部分成功:orange)';
COMMENT ON COLUMN "public"."marketplace_sync_log"."total_count" IS '总数量';
COMMENT ON COLUMN "public"."marketplace_sync_log"."success_count" IS '成功数量';
COMMENT ON COLUMN "public"."marketplace_sync_log"."failed_count" IS '失败数量';
COMMENT ON COLUMN "public"."marketplace_sync_log"."error_message" IS '错误信息';
COMMENT ON COLUMN "public"."marketplace_sync_log"."started_at" IS '开始时间';
COMMENT ON COLUMN "public"."marketplace_sync_log"."completed_at" IS '完成时间';
COMMENT ON TABLE "public"."marketplace_sync_log" IS '技能市场同步日志表';

-- ============================================================
-- 5. 创建 marketplace_download_history 表
-- ============================================================

CREATE TABLE IF NOT EXISTS "public"."marketplace_download_history" (
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
