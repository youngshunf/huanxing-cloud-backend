CREATE TABLE IF NOT EXISTS app_data_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id VARCHAR(64) NOT NULL,
    app_id VARCHAR(64) NOT NULL,
    installation_id VARCHAR(64) NOT NULL,
    install_target_type VARCHAR(32),
    install_target_id VARCHAR(64),
    resource_id VARCHAR(64) NOT NULL,
    record_key VARCHAR(255) NOT NULL,
    data_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),
    version INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_app_data_records_key UNIQUE (owner_id, app_id, installation_id, resource_id, record_key)
);

COMMENT ON TABLE app_data_records IS '应用数据记录表（JSONB 存储）';
COMMENT ON COLUMN app_data_records.id IS '主键';
COMMENT ON COLUMN app_data_records.owner_id IS 'Owner ID';
COMMENT ON COLUMN app_data_records.app_id IS 'App ID';
COMMENT ON COLUMN app_data_records.installation_id IS 'Installation ID';
COMMENT ON COLUMN app_data_records.install_target_type IS '安装目标类型';
COMMENT ON COLUMN app_data_records.install_target_id IS '安装目标 ID';
COMMENT ON COLUMN app_data_records.resource_id IS 'Resource ID';
COMMENT ON COLUMN app_data_records.record_key IS '记录键';
COMMENT ON COLUMN app_data_records.data_json IS '数据 JSON';
COMMENT ON COLUMN app_data_records.created_at IS '创建时间';
COMMENT ON COLUMN app_data_records.updated_at IS '更新时间';
COMMENT ON COLUMN app_data_records.created_by IS '创建者 ID';
COMMENT ON COLUMN app_data_records.updated_by IS '更新者 ID';
COMMENT ON COLUMN app_data_records.version IS '版本号';

CREATE INDEX idx_app_data_records_owner_app ON app_data_records(owner_id, app_id);
CREATE INDEX idx_app_data_records_installation ON app_data_records(installation_id);
CREATE INDEX idx_app_data_records_resource ON app_data_records(resource_id);
CREATE INDEX idx_app_data_records_created_at ON app_data_records(created_at);
CREATE INDEX idx_app_data_records_data_json ON app_data_records USING GIN (data_json);
