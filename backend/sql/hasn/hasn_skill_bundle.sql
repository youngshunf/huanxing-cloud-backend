-- =====================================================
-- HASN Skill Bundle 表
-- 多个 skill 的组合，供任务引用
-- =====================================================
CREATE TABLE "public"."hasn_skill_bundle" (
  "id"             bigserial PRIMARY KEY,
  "owner_id"       varchar(64) NOT NULL,
  "name"           varchar(100) NOT NULL,
  "display_name"   varchar(200),
  "description"    text,
  "skill_ids"      jsonb NOT NULL DEFAULT '[]',
  "instruction"    text,
  "created_time"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"   timestamptz(6),
  UNIQUE("owner_id", "name")
);

CREATE INDEX "idx_hasn_skill_bundle_owner" ON "public"."hasn_skill_bundle"("owner_id");

COMMENT ON TABLE "public"."hasn_skill_bundle" IS 'Skill Bundle 定义表（多个 skill 的组合）';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."owner_id" IS 'Bundle 归属 owner';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."name" IS 'Bundle 名称（唯一标识）';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."display_name" IS '显示名称';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."description" IS '描述';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."skill_ids" IS 'Skill 名称列表，如 ["github-code-review", "test-driven-development"]';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."instruction" IS '可选的额外指导语，会在加载 skills 前注入';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_skill_bundle"."updated_time" IS '更新时间';
