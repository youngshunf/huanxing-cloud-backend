-- 技能市场技能表
CREATE TABLE "public"."marketplace_skill" (
  "id" bigserial PRIMARY KEY,
  "skill_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "namespace" varchar(50) COLLATE "pg_catalog"."default",
  "slug" varchar(100) COLLATE "pg_catalog"."default",
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "name_en" varchar(200) COLLATE "pg_catalog"."default",
  "name_zh" varchar(200) COLLATE "pg_catalog"."default",
  "description" text COLLATE "pg_catalog"."default",
  "description_en" text COLLATE "pg_catalog"."default",
  "description_zh" text COLLATE "pg_catalog"."default",
  "source_language" varchar(10) COLLATE "pg_catalog"."default",
  "icon_url" varchar(500) COLLATE "pg_catalog"."default",
  "emoji" varchar(20) COLLATE "pg_catalog"."default",
  "author_id" int8,
  "author_name" varchar(100) COLLATE "pg_catalog"."default",
  "category" varchar(50) COLLATE "pg_catalog"."default",
  "tags" varchar(500) COLLATE "pg_catalog"."default",
  "source_type" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'github',
  "source_repo_url" varchar(500) COLLATE "pg_catalog"."default",
  "source_repo_path" varchar(500) COLLATE "pg_catalog"."default",
  "pricing_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'free',
  "price" numeric(10, 2) NOT NULL DEFAULT 0,
  "is_private" bool NOT NULL DEFAULT false,
  "is_official" bool NOT NULL DEFAULT false,
  "download_count" int4 NOT NULL DEFAULT 0,
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("skill_id")
);

CREATE INDEX "idx_marketplace_skill_category" ON "public"."marketplace_skill" ("category");
CREATE INDEX "idx_marketplace_skill_author_id" ON "public"."marketplace_skill" ("author_id");
CREATE INDEX "idx_marketplace_skill_pricing_type" ON "public"."marketplace_skill" ("pricing_type");
CREATE INDEX "idx_marketplace_skill_download_count" ON "public"."marketplace_skill" ("download_count" DESC);
CREATE INDEX "idx_marketplace_skill_source_type" ON "public"."marketplace_skill" ("source_type");
CREATE UNIQUE INDEX "idx_marketplace_skill_namespace_slug" ON "public"."marketplace_skill" ("namespace", "slug");

COMMENT ON COLUMN "public"."marketplace_skill"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_skill"."skill_id" IS '技能唯一标识';
COMMENT ON COLUMN "public"."marketplace_skill"."namespace" IS '命名空间（如 huanxing/clawhub）';
COMMENT ON COLUMN "public"."marketplace_skill"."slug" IS '技能标识符（如 translator-pro）';
COMMENT ON COLUMN "public"."marketplace_skill"."name" IS '技能名称';
COMMENT ON COLUMN "public"."marketplace_skill"."name_en" IS '英文名称';
COMMENT ON COLUMN "public"."marketplace_skill"."name_zh" IS '中文名称';
COMMENT ON COLUMN "public"."marketplace_skill"."description" IS '技能描述';
COMMENT ON COLUMN "public"."marketplace_skill"."description_en" IS '英文描述';
COMMENT ON COLUMN "public"."marketplace_skill"."description_zh" IS '中文描述';
COMMENT ON COLUMN "public"."marketplace_skill"."source_language" IS '源语言（en/zh，用于判断哪个是原文）';
COMMENT ON COLUMN "public"."marketplace_skill"."icon_url" IS 'SVG图标URL';
COMMENT ON COLUMN "public"."marketplace_skill"."emoji" IS 'emoji图标';
COMMENT ON COLUMN "public"."marketplace_skill"."author_id" IS '作者用户ID';
COMMENT ON COLUMN "public"."marketplace_skill"."author_name" IS '作者名称';
COMMENT ON COLUMN "public"."marketplace_skill"."category" IS '分类';
COMMENT ON COLUMN "public"."marketplace_skill"."tags" IS '标签，逗号分隔';
COMMENT ON COLUMN "public"."marketplace_skill"."source_type" IS '来源类型 (github:GitHub:blue/clawhub:ClawHub:green/local:本地:gray)';
COMMENT ON COLUMN "public"."marketplace_skill"."source_repo_url" IS '源仓库 URL';
COMMENT ON COLUMN "public"."marketplace_skill"."source_repo_path" IS '仓库内路径（如 skills/translator-pro）';
COMMENT ON COLUMN "public"."marketplace_skill"."pricing_type" IS '定价类型 (free:免费:green/paid:付费:orange)';
COMMENT ON COLUMN "public"."marketplace_skill"."price" IS '价格';
COMMENT ON COLUMN "public"."marketplace_skill"."is_private" IS '是否私有';
COMMENT ON COLUMN "public"."marketplace_skill"."is_official" IS '是否官方技能';
COMMENT ON COLUMN "public"."marketplace_skill"."download_count" IS '下载次数';
COMMENT ON TABLE "public"."marketplace_skill" IS '技能市场技能表';
