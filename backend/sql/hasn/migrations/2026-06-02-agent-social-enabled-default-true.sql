-- social_enabled 默认改为 true（社交可见默认开启，用户需手动关闭）。
-- 背景：2026-05-17 引入 social_enabled 时默认 false，导致联系人详情
--   「TA 的 AI 分身」过滤 social_enabled=true 后几乎永远为空。
--   产品决策：默认开启社交可见，用户可在分身设置里手动关闭。
-- 过滤逻辑保持不变（owned_agents 仍仅返回 social_enabled=true 的 active 分身）；
-- 前端在 human 联系人详情始终展示该区域，空集合显示「TA 还没有开启社交的 AI 分身」。

ALTER TABLE "public"."hasn_agents"
  ALTER COLUMN "social_enabled" SET DEFAULT true;

-- 存量回填：把此前默认 false 的分身全部置为社交可见。
UPDATE "public"."hasn_agents"
  SET "social_enabled" = true
  WHERE "social_enabled" IS DISTINCT FROM true;
