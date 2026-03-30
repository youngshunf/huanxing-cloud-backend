-- SOP 工作流市场表
CREATE TABLE "public"."marketplace_sop" (
  "id" bigserial PRIMARY KEY,
  "sop_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "icon_url" varchar(500) COLLATE "pg_catalog"."default",
  "emoji" varchar(20) COLLATE "pg_catalog"."default",
  "author_id" int8,
  "author_name" varchar(100) COLLATE "pg_catalog"."default",
  "category" varchar(50) COLLATE "pg_catalog"."default",
  "tags" varchar(500) COLLATE "pg_catalog"."default",
  "execution_mode" varchar(30) COLLATE "pg_catalog"."default" DEFAULT 'supervised',
  "skill_dependencies" text COLLATE "pg_catalog"."default",
  "pricing_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'free',
  "price" numeric(10, 2) NOT NULL DEFAULT 0,
  "is_private" bool NOT NULL DEFAULT false,
  "is_official" bool NOT NULL DEFAULT false,
  "download_count" int4 NOT NULL DEFAULT 0,
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("sop_id")
);

CREATE INDEX "idx_marketplace_sop_category" ON "public"."marketplace_sop" ("category");
CREATE INDEX "idx_marketplace_sop_author_id" ON "public"."marketplace_sop" ("author_id");
CREATE INDEX "idx_marketplace_sop_pricing_type" ON "public"."marketplace_sop" ("pricing_type");
CREATE INDEX "idx_marketplace_sop_download_count" ON "public"."marketplace_sop" ("download_count" DESC);

COMMENT ON COLUMN "public"."marketplace_sop"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_sop"."sop_id" IS 'SOP唯一标识';
COMMENT ON COLUMN "public"."marketplace_sop"."name" IS 'SOP名称';
COMMENT ON COLUMN "public"."marketplace_sop"."description" IS 'SOP描述';
COMMENT ON COLUMN "public"."marketplace_sop"."icon_url" IS 'SVG图标URL';
COMMENT ON COLUMN "public"."marketplace_sop"."emoji" IS 'emoji图标';
COMMENT ON COLUMN "public"."marketplace_sop"."author_id" IS '作者用户ID';
COMMENT ON COLUMN "public"."marketplace_sop"."author_name" IS '作者名称';
COMMENT ON COLUMN "public"."marketplace_sop"."category" IS '分类';
COMMENT ON COLUMN "public"."marketplace_sop"."tags" IS '标签，逗号分隔';
COMMENT ON COLUMN "public"."marketplace_sop"."execution_mode" IS '执行模式 (auto/supervised/step_by_step/deterministic)';
COMMENT ON COLUMN "public"."marketplace_sop"."skill_dependencies" IS '依赖的技能ID列表，逗号分隔';
COMMENT ON COLUMN "public"."marketplace_sop"."pricing_type" IS '定价类型';
COMMENT ON COLUMN "public"."marketplace_sop"."price" IS '价格';
COMMENT ON COLUMN "public"."marketplace_sop"."is_private" IS '是否私有';
COMMENT ON COLUMN "public"."marketplace_sop"."is_official" IS '是否官方SOP';
COMMENT ON COLUMN "public"."marketplace_sop"."download_count" IS '下载次数';
COMMENT ON TABLE "public"."marketplace_sop" IS 'SOP工作流市场表';
