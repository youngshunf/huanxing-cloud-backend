CREATE TABLE IF NOT EXISTS app_permission_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id VARCHAR(64) NOT NULL,
    installation_id VARCHAR(64) NOT NULL,
    app_id VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64),
    action VARCHAR(64) NOT NULL,
    scope VARCHAR(255) NOT NULL,
    resource_type VARCHAR(64),
    resource_id VARCHAR(255),
    result VARCHAR(32) NOT NULL,
    error_message TEXT,
    details JSONB,
    request_id VARCHAR(64),
    user_agent TEXT,
    ip_address VARCHAR(64),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE app_permission_audit_logs IS '权限审计日志表';
COMMENT ON COLUMN app_permission_audit_logs.id IS '主键';
COMMENT ON COLUMN app_permission_audit_logs.owner_id IS 'Owner ID';
COMMENT ON COLUMN app_permission_audit_logs.installation_id IS 'Installation ID';
COMMENT ON COLUMN app_permission_audit_logs.app_id IS 'App ID';
COMMENT ON COLUMN app_permission_audit_logs.agent_id IS 'Agent ID';
COMMENT ON COLUMN app_permission_audit_logs.action IS '操作类型';
COMMENT ON COLUMN app_permission_audit_logs.scope IS '权限 Scope';
COMMENT ON COLUMN app_permission_audit_logs.resource_type IS '资源类型';
COMMENT ON COLUMN app_permission_audit_logs.resource_id IS '资源 ID';
COMMENT ON COLUMN app_permission_audit_logs.result IS '结果';
COMMENT ON COLUMN app_permission_audit_logs.error_message IS '错误信息';
COMMENT ON COLUMN app_permission_audit_logs.details IS '详细信息';
COMMENT ON COLUMN app_permission_audit_logs.request_id IS '请求 ID';
COMMENT ON COLUMN app_permission_audit_logs.user_agent IS 'User Agent';
COMMENT ON COLUMN app_permission_audit_logs.ip_address IS 'IP 地址';
COMMENT ON COLUMN app_permission_audit_logs.created_at IS '创建时间';

CREATE INDEX idx_app_permission_audit_logs_owner ON app_permission_audit_logs(owner_id);
CREATE INDEX idx_app_permission_audit_logs_installation ON app_permission_audit_logs(installation_id);
CREATE INDEX idx_app_permission_audit_logs_app ON app_permission_audit_logs(app_id);
CREATE INDEX idx_app_permission_audit_logs_action ON app_permission_audit_logs(action);
CREATE INDEX idx_app_permission_audit_logs_scope ON app_permission_audit_logs(scope);
CREATE INDEX idx_app_permission_audit_logs_result ON app_permission_audit_logs(result);
CREATE INDEX idx_app_permission_audit_logs_created_at ON app_permission_audit_logs(created_at);
CREATE INDEX idx_app_permission_audit_logs_details ON app_permission_audit_logs USING GIN (details);
