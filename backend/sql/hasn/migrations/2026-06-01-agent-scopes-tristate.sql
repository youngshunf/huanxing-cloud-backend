-- Migration: hasn_agent_scopes 三态授权模型（allow/ask/deny，维度①）
-- Date: 2026-06-01
-- Design: docs/hasn-node设计文档/MCP统一工具体系/13-Agent权限模型与工具目录设计.md §3.1/§4.1 / 实施/93 P2
-- Description: 替代旧二态（scopes/denied_scopes）为三态 default_mode + capability_modes。
--              D1：三态，默认全 allow、无确认。Q3：存量行迁移后一律 default_mode='allow'。
--              仅管「维度①能力授权」；维度②对象可达性不入此表（工具运行时判定）。

ALTER TABLE hasn_agent_scopes
  ADD COLUMN IF NOT EXISTS default_mode     VARCHAR(8) NOT NULL DEFAULT 'allow',
  ADD COLUMN IF NOT EXISTS capability_modes JSONB      NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN hasn_agent_scopes.default_mode     IS '未单独配置能力的默认模式 (allow:允许:green/ask:每次询问:orange/deny:禁止:red)';
COMMENT ON COLUMN hasn_agent_scopes.capability_modes IS '每能力授权 override {capability_key: allow|ask|deny}';

-- Q3：ADD COLUMN NOT NULL DEFAULT 'allow' 已让存量行自动落 'allow'，无需额外 UPDATE。
-- 旧 scopes/denied_scopes 列保留做审计/回滚，新逻辑只读 default_mode+capability_modes。

-- Rollback:
-- ALTER TABLE hasn_agent_scopes DROP COLUMN IF EXISTS capability_modes;
-- ALTER TABLE hasn_agent_scopes DROP COLUMN IF EXISTS default_mode;
