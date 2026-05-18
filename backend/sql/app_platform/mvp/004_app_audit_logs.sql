-- =====================================================
-- AI-Native App Platform - MVP 物理表
-- 表 4/4: app_audit_logs
-- Phase: P0
-- 对应文档: docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/11-数据模型.md §2.1, §6.3
-- 协议: HExt-08 §14.4 审计日志
--
-- 设计要点:
-- - [P0] 一张表覆盖三类事件：tool_call / permission_check / event_deliver（按 event_type 区分）
-- - [P1] 按月分区；按事件类型拆出 app_tool_invocations / app_permission_audit_logs / app_event_deliveries
-- - 不外键 app_installations（ON DELETE 不应删除审计日志）
-- - context JSONB 承载 input/output/scope_diff 等差异化字段
-- =====================================================

CREATE TABLE IF NOT EXISTS app_audit_logs (
    -- 主键
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 时间（独立字段，[P1] 按月分区时作为分区键）
    "timestamp"         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 事件分类（[P0] 用 event_type 区分；[P1] 拆表）
    event_type          VARCHAR(32)     NOT NULL,
        -- 'tool_call' | 'permission_check' | 'event_deliver' | 'install' | 'uninstall' | 'scope_grant' | 'scope_revoke'

    -- 关联（不加外键，避免审计表反向阻塞业务表删除）
    owner_id            VARCHAR(64)     NOT NULL,
    app_id              VARCHAR(64)     NOT NULL,
    installation_id     VARCHAR(64),

    -- 操作主体
    actor_type          VARCHAR(32)     NOT NULL,
        -- 'owner' | 'agent' | 'app' | 'platform' | 'system'
    actor_id            VARCHAR(64)     NOT NULL,
    agent_id            VARCHAR(64),

    -- 动作（按 event_type 含义不同）
    -- tool_call:        action = tool_id
    -- permission_check: action = scope name
    -- event_deliver:    action = event_id
    action              VARCHAR(255)    NOT NULL,
    method              VARCHAR(100),

    -- 决策
    decision            VARCHAR(32)     NOT NULL,
        -- 'allow' | 'deny' | 'confirm_required'
    risk_level          VARCHAR(16),
        -- 'low' | 'medium' | 'high'

    -- 错误
    error_code          VARCHAR(64),
    error_message       TEXT,

    -- 追踪
    trace_id            VARCHAR(64),
    request_id          VARCHAR(64),

    -- 网络
    ip_address          INET,
    user_agent          TEXT,

    -- 上下文（差异化数据，event_type 不同 schema 不同）
    context             JSONB           NOT NULL DEFAULT '{}'::jsonb,

    -- 审计字段（fba codegen 约定）
    created_time        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_app_audit_logs_event_type CHECK (
        event_type IN ('tool_call', 'permission_check', 'event_deliver', 'install', 'uninstall', 'scope_grant', 'scope_revoke')
    ),
    CONSTRAINT chk_app_audit_logs_actor_type CHECK (
        actor_type IN ('owner', 'agent', 'app', 'platform', 'system')
    ),
    CONSTRAINT chk_app_audit_logs_decision CHECK (
        decision IN ('allow', 'deny', 'confirm_required')
    ),
    CONSTRAINT chk_app_audit_logs_risk_level CHECK (
        risk_level IS NULL OR risk_level IN ('low', 'medium', 'high')
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_timestamp        ON app_audit_logs("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_event_type       ON app_audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_owner_id         ON app_audit_logs(owner_id);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_app_id           ON app_audit_logs(app_id);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_installation_id  ON app_audit_logs(installation_id);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_actor            ON app_audit_logs(actor_type, actor_id);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_decision         ON app_audit_logs(decision);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_trace_id         ON app_audit_logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_app_audit_logs_error_code       ON app_audit_logs(error_code);

-- 表与列注释
COMMENT ON TABLE  app_audit_logs IS '操作审计日志表（统一记录 tool_call/permission_check/event_deliver/install 等，[P0]）';
COMMENT ON COLUMN app_audit_logs.id IS '主键';
COMMENT ON COLUMN app_audit_logs."timestamp" IS '事件时间（[P1] 按月分区键）';
COMMENT ON COLUMN app_audit_logs.event_type IS '事件类型 (tool_call:Tool调用:blue/permission_check:权限校验:purple/event_deliver:事件投递:cyan/install:安装:green/uninstall:卸载:gray/scope_grant:授权:green/scope_revoke:撤权:red)';
COMMENT ON COLUMN app_audit_logs.owner_id IS 'Owner ID';
COMMENT ON COLUMN app_audit_logs.app_id IS 'App ID';
COMMENT ON COLUMN app_audit_logs.installation_id IS 'Installation ID（可空）';
COMMENT ON COLUMN app_audit_logs.actor_type IS '操作主体类型 (owner:用户:gray/agent:Agent:blue/app:应用:purple/platform:平台:orange/system:系统:gray)';
COMMENT ON COLUMN app_audit_logs.actor_id IS '操作主体 ID';
COMMENT ON COLUMN app_audit_logs.agent_id IS '关联 Agent ID（如适用）';
COMMENT ON COLUMN app_audit_logs.action IS '动作（tool_call=tool_id, permission_check=scope, event_deliver=event_id）';
COMMENT ON COLUMN app_audit_logs.method IS 'hasn.app.* 方法名';
COMMENT ON COLUMN app_audit_logs.decision IS '决策 (allow:允许:green/deny:拒绝:red/confirm_required:需确认:orange)';
COMMENT ON COLUMN app_audit_logs.risk_level IS '风险等级 (low:低:gray/medium:中:orange/high:高:red)';
COMMENT ON COLUMN app_audit_logs.error_code IS '错误码';
COMMENT ON COLUMN app_audit_logs.error_message IS '错误消息';
COMMENT ON COLUMN app_audit_logs.trace_id IS '追踪 ID';
COMMENT ON COLUMN app_audit_logs.request_id IS '请求 ID';
COMMENT ON COLUMN app_audit_logs.ip_address IS 'IP 地址';
COMMENT ON COLUMN app_audit_logs.user_agent IS 'User-Agent';
COMMENT ON COLUMN app_audit_logs.context IS '上下文 JSONB（input/output/scope_diff 等差异化字段）';
COMMENT ON COLUMN app_audit_logs.created_time IS '记录写入时间';
