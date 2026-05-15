-- Migration: 创建 Agent 权限表
-- Date: 2026-05-13
-- Description: 创建 hasn_agent_scopes 表，用于存储 Agent 的权限配置（scopes）和业务规则

-- 创建 hasn_agent_scopes 表
CREATE TABLE IF NOT EXISTS hasn_agent_scopes (
  id              BIGSERIAL PRIMARY KEY,
  agent_hasn_id   VARCHAR(40) NOT NULL UNIQUE,
  owner_hasn_id   VARCHAR(40) NOT NULL,
  scopes          TEXT[] NOT NULL DEFAULT '{}',
  post_needs_review BOOLEAN NOT NULL DEFAULT true,
  updated_time    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_agent_scopes_owner ON hasn_agent_scopes(owner_hasn_id);

-- 添加注释
COMMENT ON TABLE hasn_agent_scopes IS 'Agent 权限配置表，存储每个 Agent 的 scopes 和业务规则';
COMMENT ON COLUMN hasn_agent_scopes.id IS '自增主键';
COMMENT ON COLUMN hasn_agent_scopes.agent_hasn_id IS 'Agent 的 HASN 唯一标识';
COMMENT ON COLUMN hasn_agent_scopes.owner_hasn_id IS '主人的 hasn_id';
COMMENT ON COLUMN hasn_agent_scopes.scopes IS '权限标识数组，如 {community.post, community.read, message.send}';
COMMENT ON COLUMN hasn_agent_scopes.post_needs_review IS '社区发布是否需要主人审核';
COMMENT ON COLUMN hasn_agent_scopes.updated_time IS '最后修改时间，用于审计和缓存失效';

-- 回滚脚本 (如需回滚，执行以下语句):
-- DROP INDEX IF EXISTS idx_agent_scopes_owner;
-- DROP TABLE IF EXISTS hasn_agent_scopes;
