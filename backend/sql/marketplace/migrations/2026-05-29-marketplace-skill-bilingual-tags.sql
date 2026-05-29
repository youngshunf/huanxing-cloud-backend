-- ============================================
-- 技能市场技能双语标签字段
-- 日期：2026-05-29
-- ============================================

BEGIN;

ALTER TABLE "public"."marketplace_skill"
  ALTER COLUMN "tags" TYPE text,
  ADD COLUMN IF NOT EXISTS "tags_en" text,
  ADD COLUMN IF NOT EXISTS "tags_zh" text;

UPDATE "public"."marketplace_skill"
SET
  "tags_en" = COALESCE("tags_en", "tags"),
  "tags_zh" = COALESCE("tags_zh", "tags")
WHERE "tags" IS NOT NULL
  AND ("tags_en" IS NULL OR "tags_zh" IS NULL);

COMMENT ON COLUMN "public"."marketplace_skill"."tags" IS '默认标签，JSON数组字符串';
COMMENT ON COLUMN "public"."marketplace_skill"."tags_en" IS '英文标签，JSON数组字符串';
COMMENT ON COLUMN "public"."marketplace_skill"."tags_zh" IS '中文标签，JSON数组字符串';

COMMIT;
