-- =====================================================
-- 2026-05-18 HASN Core/02 对齐迁移
-- 1. hasn_trade_sessions.scope 注释覆盖全部 12 个 scope 字面量
-- 2. hasn_trade_sessions 新增 lifecycle_state 字段（作用域生命周期状态机）
-- 3. hasn_contacts.trust_level 注释加 5:所有者:purple
-- =====================================================

-- ── 1. hasn_trade_sessions.scope 注释覆盖全部 12 个 scope ──
COMMENT ON COLUMN hasn_trade_sessions.scope IS '当前作用域 (commerce: pre_sale:售前/negotiation:协商/in_order:订单中/fulfilling:履约中/after_sale:售后/subscription:订阅 | service: active_order:活跃订单 | professional: consultation:咨询/treatment:进行中/follow_up:跟进 | platform: app_installation:应用安装/system_notice:系统通知)';

-- ── 2. 新增 lifecycle_state 字段 ──
ALTER TABLE hasn_trade_sessions
    ADD COLUMN IF NOT EXISTS lifecycle_state VARCHAR(16) NOT NULL DEFAULT 'active'
    CHECK (lifecycle_state IN ('pending', 'active', 'closed', 'expired'));

COMMENT ON COLUMN hasn_trade_sessions.lifecycle_state IS '作用域生命周期 (pending:待激活:gray/active:激活:violet/closed:已关闭:neutral/expired:已过期:red)';

CREATE INDEX IF NOT EXISTS idx_hasn_trade_sessions_lifecycle ON hasn_trade_sessions(lifecycle_state);

-- ── 3. 同步 hasn_contacts.trust_level 注释 ──
COMMENT ON COLUMN hasn_contacts.trust_level IS '信任等级 (0:已拉黑:red/1:陌生人:gray/2:普通联系人:blue/3:朋友:green/4:高信任:orange/5:所有者:purple)';
