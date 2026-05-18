-- =====================================================
-- AI-Native App Platform - MVP 物理表
-- 表 3/4: app_data_records
-- Phase: P0
-- 对应文档: docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/11-数据模型.md §2.1
-- 协议: HExt-08 §6 Resource
--
-- 设计要点:
-- - 隔离键: owner_id + app_id + installation_id + resource_id + record_key
-- - resource_id 不外键 app_resources（[P1] 落表后再补 FK）
-- - data_json JSONB 存储灵活 schema，[P2] 高频访问 Resource 升级为专用物理表
-- - install_target_type/_id 与 app_installations 对齐
-- =====================================================

CREATE TABLE IF NOT EXISTS app_data_records (
    -- 主键
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 隔离键
    owner_id            VARCHAR(64)     NOT NULL,
    app_id              VARCHAR(64)     NOT NULL,
    installation_id     VARCHAR(64)     NOT NULL,

    -- 安装目标（与 app_installations 对齐，冗余便于按目标查）
    install_target_type VARCHAR(32),
    install_target_id   VARCHAR(64),

    -- Resource 定位
    resource_id         VARCHAR(64)     NOT NULL,
    record_key          VARCHAR(255)    NOT NULL,

    -- 数据（JSONB）
    data_json           JSONB           NOT NULL,

    -- 版本（乐观锁）
    version             INTEGER         NOT NULL DEFAULT 1,

    -- 操作者
    created_by          VARCHAR(64),
    updated_by          VARCHAR(64),

    -- 审计字段（fba codegen 约定）
    created_time        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time        TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT chk_app_data_records_install_target_type CHECK (
        install_target_type IS NULL OR install_target_type IN ('owner', 'agent', 'constellation')
    ),
    CONSTRAINT fk_app_data_records_installation
        FOREIGN KEY (installation_id) REFERENCES app_installations(installation_id) ON DELETE CASCADE,
    CONSTRAINT uk_app_data_records_key UNIQUE (owner_id, app_id, installation_id, resource_id, record_key)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_app_data_records_owner_app     ON app_data_records(owner_id, app_id);
CREATE INDEX IF NOT EXISTS idx_app_data_records_installation  ON app_data_records(installation_id);
CREATE INDEX IF NOT EXISTS idx_app_data_records_resource      ON app_data_records(resource_id);
CREATE INDEX IF NOT EXISTS idx_app_data_records_target        ON app_data_records(install_target_type, install_target_id);
CREATE INDEX IF NOT EXISTS idx_app_data_records_created_time  ON app_data_records(created_time DESC);
CREATE INDEX IF NOT EXISTS idx_app_data_records_data_json_gin ON app_data_records USING GIN (data_json);

-- 表与列注释
COMMENT ON TABLE  app_data_records IS '应用数据记录表（JSONB 存储，[P0]）';
COMMENT ON COLUMN app_data_records.id IS '主键';
COMMENT ON COLUMN app_data_records.owner_id IS 'Owner ID（数据隔离键）';
COMMENT ON COLUMN app_data_records.app_id IS 'App ID（数据隔离键）';
COMMENT ON COLUMN app_data_records.installation_id IS 'Installation ID（数据隔离键）';
COMMENT ON COLUMN app_data_records.install_target_type IS '安装目标类型 (owner:owner:gray/agent:agent:blue/constellation:星座:purple)';
COMMENT ON COLUMN app_data_records.install_target_id IS '安装目标 ID';
COMMENT ON COLUMN app_data_records.resource_id IS 'Resource ID（来自 manifest.resources[].resource_id；[P1] 外键 app_resources）';
COMMENT ON COLUMN app_data_records.record_key IS '记录键（应用自定义）';
COMMENT ON COLUMN app_data_records.data_json IS '数据内容（JSONB）';
COMMENT ON COLUMN app_data_records.version IS '乐观锁版本号';
COMMENT ON COLUMN app_data_records.created_by IS '创建者 ID';
COMMENT ON COLUMN app_data_records.updated_by IS '更新者 ID';
COMMENT ON COLUMN app_data_records.created_time IS '创建时间';
COMMENT ON COLUMN app_data_records.updated_time IS '更新时间';
