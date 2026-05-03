-- 配合 §07 Tier 1 决策（A5 + A2）：
--   * hermes_agent.template 从 varchar(32) 扩到 varchar(64)，
--     字典注释从枚举（assistant/office/creator/custom）改为 marketplace_app.app_id
--   * marketplace_app 新增 app_type 列，区分 agent_template / skill_pack / sop_pack
-- 关联 commit：
--   * huanxing-hub@35f2bdb（IDENTITY → SOUL 合并）
--   * huanxing-project §07 Tier 1 同步
-- 2026-05-03

-- =============================================================
-- 1) hermes_agent.template
-- =============================================================
ALTER TABLE "public"."hermes_agent"
  ALTER COLUMN "template" TYPE varchar(64);

COMMENT ON COLUMN "public"."hermes_agent"."template"
  IS '模板 ID（云端 marketplace_app.app_id 快照，例：assistant / media-creator / finance / side-hustle / custom）';

-- =============================================================
-- 2) marketplace_app.app_type
-- =============================================================
ALTER TABLE "public"."marketplace_app"
  ADD COLUMN IF NOT EXISTS "app_type" varchar(20) NOT NULL DEFAULT 'agent_template';

-- 历史数据兜底：现存 marketplace_app 都是 agent_template
UPDATE "public"."marketplace_app"
   SET "app_type" = 'agent_template'
 WHERE "app_type" IS NULL OR "app_type" = '';

COMMENT ON COLUMN "public"."marketplace_app"."app_type"
  IS '应用类型 (agent_template:Agent模板:blue/skill_pack:技能包:cyan/sop_pack:SOP包:purple)';

CREATE INDEX IF NOT EXISTS "idx_marketplace_app_app_type"
  ON "public"."marketplace_app" ("app_type");
