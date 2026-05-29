-- 个人社区设置（doc-13 §2.3.1）：公开边界/默认评论策略/通知开关
-- 一个用户一份配置，JSONB 加列（无新表）。
ALTER TABLE "public"."hasn_humans"
  ADD COLUMN IF NOT EXISTS "community_settings" jsonb NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN "public"."hasn_humans"."community_settings" IS
  '社区个人设置 (JSONB)：公开边界/默认评论策略/通知开关';
