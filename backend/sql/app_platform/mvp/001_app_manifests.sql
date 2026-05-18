-- =====================================================
-- AI-Native App Platform - MVP 物理表
-- 表 1/4: app_manifests
-- Phase: P0
-- 对应文档: docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/11-数据模型.md §2.1, §4.2
-- 协议: HExt-08 §3 App Manifest
--
-- 设计要点:
-- - manifest_jsonb 内嵌 tools/resources/events/version 等子结构，[P1] 前不拆子表
-- - placeholder 字段（marketplace.*, pricing_model, public_service_enabled）原样存在 manifest_jsonb 中，[P0] 解析但不验证
-- - status 仅保留 draft/installable/revoked 三态，[P1] 扩展开发态/审核态
-- - owner_id 即作者，无独立 developer 表（[P2] 引入 app_developers）
-- =====================================================

CREATE TABLE IF NOT EXISTS app_manifests (
    -- 主键
    app_id              VARCHAR(64)     PRIMARY KEY,

    -- 所有者（[P0] 即作者）
    owner_id            VARCHAR(64)     NOT NULL,

    -- 命名空间与名称
    namespace           VARCHAR(64)     NOT NULL,
    name                VARCHAR(64)     NOT NULL,
    display_name        VARCHAR(128)    NOT NULL,
    description         TEXT,
    icon_url            VARCHAR(500),

    -- 当前生效版本（[P0] 用 manifest hash，[P1] 拆 app_versions 表）
    current_version     VARCHAR(50)     NOT NULL,

    -- Manifest 全量内容（事实源，包含 tools/resources/events/scopes/frontend/marketplace placeholder 等所有子结构）
    manifest_jsonb      JSONB           NOT NULL,

    -- 后端运行模式（[P0] 仅 platform_hosted，[P1] 引入 external_hosted）
    backend_runtime_mode VARCHAR(32)    NOT NULL DEFAULT 'platform_hosted',

    -- 前端托管模式（[P0] 仅 none/platform_hosted）
    frontend_hosting_mode VARCHAR(32)   NOT NULL DEFAULT 'none',

    -- 分类与标签（冗余出来便于查询，事实源仍在 manifest_jsonb）
    category            VARCHAR(64),
    tags                JSONB           NOT NULL DEFAULT '[]'::jsonb,

    -- 状态 (draft:草稿:gray/installable:可安装:green/revoked:已下架:red)
    status              VARCHAR(32)     NOT NULL DEFAULT 'draft',

    -- 审计字段（fba codegen 约定）
    created_time        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time        TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT chk_app_manifests_app_id_format CHECK (
        app_id ~ '^app_[a-z0-9_]+$'
    ),
    CONSTRAINT chk_app_manifests_backend_runtime_mode CHECK (
        backend_runtime_mode IN ('platform_hosted', 'external_hosted')
    ),
    CONSTRAINT chk_app_manifests_frontend_hosting_mode CHECK (
        frontend_hosting_mode IN ('none', 'platform_hosted', 'external_hosted')
    ),
    CONSTRAINT chk_app_manifests_status CHECK (
        status IN ('draft', 'installable', 'revoked')
    ),
    CONSTRAINT uk_app_manifests_namespace_name UNIQUE (namespace, name)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_app_manifests_owner_id     ON app_manifests(owner_id);
CREATE INDEX IF NOT EXISTS idx_app_manifests_status       ON app_manifests(status);
CREATE INDEX IF NOT EXISTS idx_app_manifests_category     ON app_manifests(category);
CREATE INDEX IF NOT EXISTS idx_app_manifests_created_time ON app_manifests(created_time DESC);
CREATE INDEX IF NOT EXISTS idx_app_manifests_manifest_gin ON app_manifests USING GIN (manifest_jsonb);

-- 表与列注释
COMMENT ON TABLE  app_manifests IS 'App 本体表：Manifest 事实源（[P0]）';
COMMENT ON COLUMN app_manifests.app_id IS 'App ID，格式 app_{namespace}_{name}';
COMMENT ON COLUMN app_manifests.owner_id IS 'Owner ID（[P0] 即作者；[P2] 引入独立 developer_id）';
COMMENT ON COLUMN app_manifests.namespace IS 'Manifest 命名空间';
COMMENT ON COLUMN app_manifests.name IS 'App 名称';
COMMENT ON COLUMN app_manifests.display_name IS '展示名称';
COMMENT ON COLUMN app_manifests.description IS '描述';
COMMENT ON COLUMN app_manifests.icon_url IS '图标 URL';
COMMENT ON COLUMN app_manifests.current_version IS '当前生效版本号（[P0] manifest hash）';
COMMENT ON COLUMN app_manifests.manifest_jsonb IS 'Manifest 全量 JSONB（包含 tools/resources/events/scopes/frontend/marketplace 等）';
COMMENT ON COLUMN app_manifests.backend_runtime_mode IS '后端运行模式：platform_hosted/external_hosted';
COMMENT ON COLUMN app_manifests.frontend_hosting_mode IS '前端托管模式：none/platform_hosted/external_hosted';
COMMENT ON COLUMN app_manifests.category IS '分类';
COMMENT ON COLUMN app_manifests.tags IS '标签数组（JSONB）';
COMMENT ON COLUMN app_manifests.status IS '状态 (draft:草稿:gray/installable:可安装:green/revoked:已下架:red)';
COMMENT ON COLUMN app_manifests.created_time IS '创建时间';
COMMENT ON COLUMN app_manifests.updated_time IS '更新时间';
