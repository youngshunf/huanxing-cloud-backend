-- Migration: 统一 Agent scope 词表（点号 → 冒号）
-- Date: 2026-06-01
-- Design: docs/hasn-node设计文档/MCP统一工具体系/13-Agent权限模型与工具目录设计.md §3.3 / 实施/93 P1
-- Description: hasn_agent_scopes.scopes 存量行把 `domain.action` 一次性改写为 `domain:action`，
--              与全栈统一冒号词表对齐（OAuth/MCP 惯例，也是平台工具现状）。
--              迁移期判定函数仍保留点/冒号归一兜底，全栈切完再撤。

UPDATE hasn_agent_scopes
SET scopes = COALESCE(
    (SELECT array_agg(replace(s, '.', ':')) FROM unnest(scopes) AS s),
    '{}'
)
WHERE EXISTS (SELECT 1 FROM unnest(scopes) AS s WHERE s LIKE '%.%');

-- Rollback（反向 replace；仅迁移窗口内、确认无新写入冒号语义后使用）:
-- UPDATE hasn_agent_scopes
-- SET scopes = COALESCE((SELECT array_agg(replace(s, ':', '.')) FROM unnest(scopes) AS s), '{}')
-- WHERE EXISTS (SELECT 1 FROM unnest(scopes) AS s WHERE s LIKE '%:%');
