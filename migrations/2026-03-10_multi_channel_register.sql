-- 多渠道统一注册 — 数据库迁移脚本
-- 日期: 2026-03-10
-- 注意: 在生产执行前先备份！

-- 1. subscription_tier 加 max_agents
ALTER TABLE huanxing.subscription_tier
  ADD COLUMN IF NOT EXISTS max_agents INT NOT NULL DEFAULT 1;

UPDATE huanxing.subscription_tier SET max_agents = 1 WHERE tier_name = 'free' AND app_code = 'huanxing';
UPDATE huanxing.subscription_tier SET max_agents = 2 WHERE tier_name = 'pro' AND app_code = 'huanxing';
UPDATE huanxing.subscription_tier SET max_agents = 5 WHERE tier_name = 'advanced' AND app_code = 'huanxing';
UPDATE huanxing.subscription_tier SET max_agents = 10 WHERE tier_name = 'flagship' AND app_code = 'huanxing';

-- 2. user_subscription 加 max_agents
ALTER TABLE huanxing.user_subscription
  ADD COLUMN IF NOT EXISTS max_agents INT NOT NULL DEFAULT 1;

-- 按现有订阅等级初始化
UPDATE huanxing.user_subscription us
SET max_agents = st.max_agents
FROM huanxing.subscription_tier st
WHERE us.tier = st.tier_name AND us.app_code = st.app_code;

-- 3. huanxing_user 加唯一约束（先检查有无重复数据）
-- 查重复数据:
-- SELECT user_id, server_id, COUNT(*) FROM huanxing.huanxing_user GROUP BY user_id, server_id HAVING COUNT(*) > 1;
-- 如果有重复，手动清理后再加约束

ALTER TABLE huanxing.huanxing_user
  ADD CONSTRAINT uq_huanxing_user_server UNIQUE (user_id, server_id);
