-- 技能市场模板表（Agent模板/技能包/SOP包）
CREATE TABLE "public"."marketplace_template" (
  "id" bigserial PRIMARY KEY,
  "template_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "namespace" varchar(50) COLLATE "pg_catalog"."default",
  "slug" varchar(100) COLLATE "pg_catalog"."default",
  "template_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'agent_template',
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
  "pricing_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'free',
  "price" numeric(10, 2) NOT NULL DEFAULT 0,
  "is_private" bool NOT NULL DEFAULT false,
  "is_official" bool NOT NULL DEFAULT false,
  "download_count" int4 NOT NULL DEFAULT 0,
  "category" varchar(50) COLLATE "pg_catalog"."default",
  "tags" varchar(500) COLLATE "pg_catalog"."default",
  "source_type" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'github',
  "source_repo_url" varchar(500) COLLATE "pg_catalog"."default",
  "source_repo_path" varchar(500) COLLATE "pg_catalog"."default",
  "skill_dependencies" text COLLATE "pg_catalog"."default",
  "sop_dependencies" text COLLATE "pg_catalog"."default",
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("template_id")
);

CREATE INDEX "idx_marketplace_template_author_id" ON "public"."marketplace_template" ("author_id");
CREATE INDEX "idx_marketplace_template_pricing_type" ON "public"."marketplace_template" ("pricing_type");
CREATE INDEX "idx_marketplace_template_download_count" ON "public"."marketplace_template" ("download_count" DESC);
CREATE INDEX "idx_marketplace_template_template_type" ON "public"."marketplace_template" ("template_type");
CREATE UNIQUE INDEX "idx_marketplace_template_namespace_slug" ON "public"."marketplace_template" ("namespace", "slug");

COMMENT ON COLUMN "public"."marketplace_template"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_template"."template_id" IS '模板唯一标识';
COMMENT ON COLUMN "public"."marketplace_template"."namespace" IS '命名空间（如 huanxing/clawhub）';
COMMENT ON COLUMN "public"."marketplace_template"."slug" IS '模板标识符';
COMMENT ON COLUMN "public"."marketplace_template"."template_type" IS '模板类型 (agent_template:Agent模板:blue/skill_pack:技能包:cyan/sop_pack:SOP包:purple)';
COMMENT ON COLUMN "public"."marketplace_template"."name" IS '模板名称';
COMMENT ON COLUMN "public"."marketplace_template"."name_en" IS '英文名称';
COMMENT ON COLUMN "public"."marketplace_template"."name_zh" IS '中文名称';
COMMENT ON COLUMN "public"."marketplace_template"."description" IS '模板描述';
COMMENT ON COLUMN "public"."marketplace_template"."description_en" IS '英文描述';
COMMENT ON COLUMN "public"."marketplace_template"."description_zh" IS '中文描述';
COMMENT ON COLUMN "public"."marketplace_template"."source_language" IS '源语言（en/zh，用于判断哪个是原文）';
COMMENT ON COLUMN "public"."marketplace_template"."icon_url" IS '模板图标URL';
COMMENT ON COLUMN "public"."marketplace_template"."emoji" IS 'emoji图标';
COMMENT ON COLUMN "public"."marketplace_template"."author_id" IS '作者用户ID';
COMMENT ON COLUMN "public"."marketplace_template"."author_name" IS '作者名称';
COMMENT ON COLUMN "public"."marketplace_template"."pricing_type" IS '定价类型 (free:免费:green/paid:付费:orange/subscription:订阅:blue)';
COMMENT ON COLUMN "public"."marketplace_template"."price" IS '价格';
COMMENT ON COLUMN "public"."marketplace_template"."is_private" IS '是否私有';
COMMENT ON COLUMN "public"."marketplace_template"."is_official" IS '是否官方模板';
COMMENT ON COLUMN "public"."marketplace_template"."download_count" IS '下载次数';
COMMENT ON COLUMN "public"."marketplace_template"."category" IS '分类';
COMMENT ON COLUMN "public"."marketplace_template"."tags" IS '标签，逗号分隔';
COMMENT ON COLUMN "public"."marketplace_template"."source_type" IS '来源类型 (github:GitHub:blue/clawhub:ClawHub:green/local:本地:gray)';
COMMENT ON COLUMN "public"."marketplace_template"."source_repo_url" IS '源仓库 URL';
COMMENT ON COLUMN "public"."marketplace_template"."source_repo_path" IS '仓库内路径';
COMMENT ON COLUMN "public"."marketplace_template"."skill_dependencies" IS '依赖的技能ID列表，逗号分隔';
COMMENT ON COLUMN "public"."marketplace_template"."sop_dependencies" IS '依赖的SOP ID列表，逗号分隔';
COMMENT ON TABLE "public"."marketplace_template" IS '技能市场模板表（Agent模板/技能包/SOP包）';
