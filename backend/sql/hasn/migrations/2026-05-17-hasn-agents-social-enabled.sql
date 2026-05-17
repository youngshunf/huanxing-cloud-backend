-- 为 hasn_agents 增加 social_enabled，标识 Agent 是否对外开启社交可见
-- 用于联系人详情过滤 owned_agents：仅返回 social_enabled = true 的 Agent

ALTER TABLE "public"."hasn_agents"
  ADD COLUMN IF NOT EXISTS "social_enabled" boolean NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_hasn_agents_owner_social
  ON "public"."hasn_agents"(owner_id, social_enabled)
  WHERE status = 'active' AND deleted_at IS NULL;

COMMENT ON COLUMN "public"."hasn_agents"."social_enabled"
  IS '是否对外开启社交可见 (true:社交可见/false:仅自用)';
