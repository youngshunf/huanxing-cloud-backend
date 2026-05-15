-- app_data_records 表
-- 应用数据记录表（JSONB 存储）
-- Phase 1: 使用 JSONB 存储灵活 schema 的数据
-- Phase 2+: 高频访问的 Resource 可升级为专用物理表

CREATE TABLE IF NOT EXISTS app_data_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 隔离键
    owner_id VARCHAR(64) NOT NULL,
    app_id VARCHAR(64) NOT NULL,
    installation_id VARCHAR(64) NOT NULL,

    -- 唤星扩展：安装目标（可选）
    install_target_type VARCHAR(32),
    install_target_id VARCHAR(64),

    -- Resource 信息
    resource_id VARCHAR(64) NOT NULL,
    record_key VARCHAR(255) NOT NULL,

    -- 数据存储
    data_json JSONB NOT NULL,

    -- 元数据
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    updated_by VARCHAR(64),

    -- 版本控制（可选）
    version INTEGER NOT NULL DEFAULT 1,

    -- 唯一约束：同一个 installation 下，同一个 resource 的 record_key 唯一
    CONSTRAINT uk_app_data_records_key UNIQUE (owner_id, app_id, installation_id, resource_id, record_key)
);

-- 表注释
COMMENT ON TABLE app_data_records IS '应用数据记录表（JSONB 存储）';

-- 列注释
COMMENT ON COLUMN app_data_records.id IS '主键';
COMMENT ON COLUMN app_data_records.owner_id IS 'Owner ID';
COMMENT ON COLUMN app_data_records.app_id IS 'App ID';
COMMENT ON COLUMN app_data_records.installation_id IS 'Installation ID';
COMMENT ON COLUMN app_data_records.install_target_type IS '安装目标类型（agent, constellation 等）';
COMMENT ON COLUMN app_data_records.install_target_id IS '安装目标 ID';
COMMENT ON COLUMN app_data_records.resource_id IS 'Resource ID（来自 app_resources 表）';
COMMENT ON COLUMN app_data_records.record_key IS '记录键（应用自定义）';
COMMENT ON COLUMN app_data_records.data_json IS '数据 JSON';
COMMENT ON COLUMN app_data_records.created_at IS '创建时间';
COMMENT ON COLUMN app_data_records.updated_at IS '更新时间';
COMMENT ON COLUMN app_data_records.created_by IS '创建者 ID';
COMMENT ON COLUMN app_data_records.updated_by IS '更新者 ID';
COMMENT ON COLUMN app_data_records.version IS '版本号';

-- 索引
CREATE INDEX idx_app_data_records_owner_app ON app_data_records(owner_id, app_id);
CREATE INDEX idx_app_data_records_installation ON app_data_records(installation_id);
CREATE INDEX idx_app_data_records_resource ON app_data_records(resource_id);
CREATE INDEX idx_app_data_records_created_at ON app_data_records(created_at);

-- GIN 索引用于 JSONB 查询
CREATE INDEX idx_app_data_records_data_json ON app_data_records USING GIN (data_json);

-- 外键约束
ALTER TABLE app_data_records
    ADD CONSTRAINT fk_app_data_records_installation
    FOREIGN KEY (installation_id) REFERENCES app_installations(installation_id)
    ON DELETE CASCADE;

ALTER TABLE app_data_records
    ADD CONSTRAINT fk_app_data_records_resource
    FOREIGN KEY (resource_id) REFERENCES app_resources(resource_id)
    ON DELETE CASCADE;

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_app_data_records_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_app_data_records_updated_at
    BEFORE UPDATE ON app_data_records
    FOR EACH ROW
    EXECUTE FUNCTION update_app_data_records_updated_at();
