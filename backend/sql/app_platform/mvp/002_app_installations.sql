-- =====================================================
-- AI-Native App Platform - MVP 物理表
-- 表 2/4: app_installations
-- Phase: P0
-- 对应文档: docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/11-数据模型.md §2.1, §4.5
-- 协议: HExt-08 §5 Installation
--
-- 设计要点:
-- - install_target_type/_id 表达"装到 owner/agent/constellation"三种目标，[P0] 即支持
-- - granted_scopes 是 JSONB 字符串数组，承载所有 scope 授予（[P1] 拆 app_permission_grants 表）
-- - listing_id / entitlement_id 是 [P2] 公开市场字段，[P0] 保留 nullable 占位
-- - status [P0] 仅 active/revoked；update_available/pending_reauth/suspended 是 [P1] 状态机扩展
-- - 不外键 app_listings，避免 [P0] 强依赖 [P2] 表
-- =====================================================

CREATE TABLE IF NOT EXISTS app_installations (
    -- 主键
    installation_id     VARCHAR(64)     PRIMARY KEY,

    -- 关联
    owner_id            VARCHAR(64)     NOT NULL,
    app_id              VARCHAR(64)     NOT NULL,

    -- 安装目标（[P0] 即支持三种目标）
    install_target_type VARCHAR(32)     NOT NULL,
    install_target_id   VARCHAR(64)     NOT NULL,

    -- 安装的版本
    installed_version   VARCHAR(50)     NOT NULL,

    -- 授予的权限（JSONB 字符串数组；[P1] 拆 app_permission_grants 表）
    granted_scopes      JSONB           NOT NULL DEFAULT '[]'::jsonb,

    -- 状态 (active:活跃:green/revoked:已撤销:red)
    -- [P1] 扩展为：active/update_available/pending_reauth/suspended/revoked
    status              VARCHAR(32)     NOT NULL DEFAULT 'active',

    -- [P2] 公开市场字段（[P0] 保留 nullable 占位）
    listing_id          UUID,
    entitlement_id      VARCHAR(64),

    -- 安装/使用时间
    installed_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at        TIMESTAMP WITH TIME ZONE,

    -- 撤销信息
    revoked_at          TIMESTAMP WITH TIME ZONE,
    revocation_reason   TEXT,

    -- 审计字段（fba codegen 约定）
    created_time        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time        TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT chk_app_installations_installation_id_format CHECK (
        installation_id ~ '^appi_[a-z0-9_-]+$'
    ),
    CONSTRAINT chk_app_installations_install_target_type CHECK (
        install_target_type IN ('owner', 'agent', 'constellation')
    ),
    CONSTRAINT chk_app_installations_status CHECK (
        status IN ('active', 'revoked')
    ),
    CONSTRAINT fk_app_installations_app
        FOREIGN KEY (app_id) REFERENCES app_manifests(app_id) ON DELETE RESTRICT,
    CONSTRAINT uk_app_installations_owner_target_app UNIQUE (owner_id, app_id, install_target_type, install_target_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_app_installations_owner_id        ON app_installations(owner_id);
CREATE INDEX IF NOT EXISTS idx_app_installations_app_id          ON app_installations(app_id);
CREATE INDEX IF NOT EXISTS idx_app_installations_target          ON app_installations(install_target_type, install_target_id);
CREATE INDEX IF NOT EXISTS idx_app_installations_status          ON app_installations(status);
CREATE INDEX IF NOT EXISTS idx_app_installations_owner_app       ON app_installations(owner_id, app_id);
CREATE INDEX IF NOT EXISTS idx_app_installations_installed_at    ON app_installations(installed_at DESC);
CREATE INDEX IF NOT EXISTS idx_app_installations_granted_scopes  ON app_installations USING GIN (granted_scopes);

-- 表与列注释
COMMENT ON TABLE  app_installations IS 'App 安装记录表（[P0]）';
COMMENT ON COLUMN app_installations.installation_id IS 'Installation ID，格式 appi_{uuid}';
COMMENT ON COLUMN app_installations.owner_id IS 'Owner ID';
COMMENT ON COLUMN app_installations.app_id IS '关联 App';
COMMENT ON COLUMN app_installations.install_target_type IS '安装目标类型 (owner:owner:gray/agent:agent:blue/constellation:星座:purple)';
COMMENT ON COLUMN app_installations.install_target_id IS '安装目标 ID';
COMMENT ON COLUMN app_installations.installed_version IS '安装的 App 版本';
COMMENT ON COLUMN app_installations.granted_scopes IS 'Owner 授予的权限列表（JSONB 字符串数组）';
COMMENT ON COLUMN app_installations.status IS '状态 (active:活跃:green/revoked:已撤销:red)';
COMMENT ON COLUMN app_installations.listing_id IS '[P2 placeholder] 关联 app_listings.listing_id';
COMMENT ON COLUMN app_installations.entitlement_id IS '[P2 placeholder] 关联 app_entitlements.entitlement_id';
COMMENT ON COLUMN app_installations.installed_at IS '安装时间';
COMMENT ON COLUMN app_installations.last_used_at IS '最近使用时间';
COMMENT ON COLUMN app_installations.revoked_at IS '撤销时间';
COMMENT ON COLUMN app_installations.revocation_reason IS '撤销原因';
COMMENT ON COLUMN app_installations.created_time IS '创建时间';
COMMENT ON COLUMN app_installations.updated_time IS '更新时间';
