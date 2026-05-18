-- ============================================================================
-- AI-Native 应用平台 - 应用核心表（简化版 Phase 1）
-- ============================================================================
-- 文件: 005_create_app_core_tables.sql
-- 描述: 应用核心表（11 张）- Phase 1 最小闭环版本
-- 参考: docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/11-数据模型.md
-- 作者: 唤星项目
-- 日期: 2026-05-14
-- ============================================================================

-- ============================================================================
-- 表 1: app_developers - 开发者表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_developers" (
    -- 主键
    "developer_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 基本信息
    "owner_id" VARCHAR(255) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "company_name" VARCHAR(255),
    "website_url" VARCHAR(500),

    -- 认证状态
    "verification_status" VARCHAR(50) NOT NULL DEFAULT 'unverified',
    "verified_at" TIMESTAMP,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_developers_verification_status" CHECK (
        "verification_status" IN ('unverified', 'pending', 'verified', 'rejected')
    ),
    CONSTRAINT "chk_app_developers_status" CHECK (
        "status" IN ('active', 'suspended', 'banned')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_developers_owner_id" ON "public"."app_developers"("owner_id");
CREATE INDEX IF NOT EXISTS "idx_app_developers_email" ON "public"."app_developers"("email");
CREATE INDEX IF NOT EXISTS "idx_app_developers_status" ON "public"."app_developers"("status");

COMMENT ON TABLE "public"."app_developers" IS '应用开发者表';
COMMENT ON COLUMN "public"."app_developers"."developer_id" IS '开发者 ID';
COMMENT ON COLUMN "public"."app_developers"."owner_id" IS '关联的 Owner ID';
COMMENT ON COLUMN "public"."app_developers"."display_name" IS '显示名称';
COMMENT ON COLUMN "public"."app_developers"."email" IS '邮箱';
COMMENT ON COLUMN "public"."app_developers"."verification_status" IS '认证状态 (unverified:未认证:gray/pending:待审核:blue/verified:已认证:green/rejected:已拒绝:red)';
COMMENT ON COLUMN "public"."app_developers"."status" IS '状态 (active:活跃:green/suspended:暂停:orange/banned:封禁:red)';

-- ============================================================================
-- 表 2: app_manifests - App 清单表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_manifests" (
    -- 主键
    "app_id" VARCHAR(255) PRIMARY KEY,

    -- 基本信息
    "developer_id" UUID NOT NULL,
    "namespace" VARCHAR(100) NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "icon_url" VARCHAR(500),

    -- 版本信息
    "current_version" VARCHAR(50) NOT NULL,

    -- 运行模式
    "backend_runtime_mode" VARCHAR(50) NOT NULL DEFAULT 'platform_hosted',
    "frontend_hosting_mode" VARCHAR(50) NOT NULL DEFAULT 'none',

    -- 权限声明
    "requested_scopes" JSONB NOT NULL DEFAULT '[]',

    -- 分类
    "category" VARCHAR(100),
    "tags" JSONB DEFAULT '[]',

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'draft',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_manifests_app_id_format" CHECK (
        "app_id" ~ '^app_[a-z0-9_]+$'
    ),
    CONSTRAINT "chk_app_manifests_backend_runtime_mode" CHECK (
        "backend_runtime_mode" IN ('platform_hosted', 'external_hosted')
    ),
    CONSTRAINT "chk_app_manifests_frontend_hosting_mode" CHECK (
        "frontend_hosting_mode" IN ('none', 'platform_hosted', 'external_hosted')
    ),
    CONSTRAINT "chk_app_manifests_status" CHECK (
        "status" IN ('draft', 'submitted', 'approved', 'rejected', 'published', 'archived')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_manifests_namespace_name" ON "public"."app_manifests"("namespace", "name");
CREATE INDEX IF NOT EXISTS "idx_app_manifests_developer_id" ON "public"."app_manifests"("developer_id");
CREATE INDEX IF NOT EXISTS "idx_app_manifests_status" ON "public"."app_manifests"("status");

COMMENT ON TABLE "public"."app_manifests" IS 'App 清单表';
COMMENT ON COLUMN "public"."app_manifests"."app_id" IS 'App ID';
COMMENT ON COLUMN "public"."app_manifests"."developer_id" IS '开发者 ID';
COMMENT ON COLUMN "public"."app_manifests"."display_name" IS '显示名称';
COMMENT ON COLUMN "public"."app_manifests"."backend_runtime_mode" IS '后端运行模式 (platform_hosted:平台托管:blue/external_hosted:外部托管:green)';
COMMENT ON COLUMN "public"."app_manifests"."frontend_hosting_mode" IS '前端托管模式 (none:无前端:gray/platform_hosted:平台托管:blue/external_hosted:外部托管:green)';
COMMENT ON COLUMN "public"."app_manifests"."status" IS '状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/archived:已归档:gray)';

-- ============================================================================
-- 表 3: app_versions - App 版本表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_versions" (
    -- 主键
    "version_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version" VARCHAR(50) NOT NULL,

    -- 版本信息
    "changelog" TEXT,
    "manifest_snapshot" JSONB NOT NULL,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'draft',

    -- 发布信息
    "published_at" TIMESTAMP,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_versions_status" CHECK (
        "status" IN ('draft', 'submitted', 'approved', 'rejected', 'published', 'deprecated')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_versions_app_version" ON "public"."app_versions"("app_id", "version");
CREATE INDEX IF NOT EXISTS "idx_app_versions_app_id" ON "public"."app_versions"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_versions_status" ON "public"."app_versions"("status");

COMMENT ON TABLE "public"."app_versions" IS 'App 版本表';
COMMENT ON COLUMN "public"."app_versions"."version_id" IS '版本 ID';
COMMENT ON COLUMN "public"."app_versions"."app_id" IS 'App ID';
COMMENT ON COLUMN "public"."app_versions"."version" IS '版本号';
COMMENT ON COLUMN "public"."app_versions"."manifest_snapshot" IS 'Manifest 快照（JSONB）';
COMMENT ON COLUMN "public"."app_versions"."status" IS '状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/deprecated:已废弃:orange)';

-- ============================================================================
-- 表 4: app_listings - 应用市场列表表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_listings" (
    -- 主键
    "listing_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 可见性
    "visibility" VARCHAR(50) NOT NULL DEFAULT 'private',

    -- 市场信息
    "title" VARCHAR(255) NOT NULL,
    "description_long" TEXT NOT NULL,

    -- 定价
    "pricing_model" VARCHAR(50) NOT NULL DEFAULT 'free',
    "price_amount" DECIMAL(10, 2),

    -- 统计
    "install_count" INTEGER NOT NULL DEFAULT 0,
    "rating_average" DECIMAL(3, 2),

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'draft',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_listings_visibility" CHECK (
        "visibility" IN ('private', 'public')
    ),
    CONSTRAINT "chk_app_listings_pricing_model" CHECK (
        "pricing_model" IN ('free', 'one_time', 'subscription', 'usage_based')
    ),
    CONSTRAINT "chk_app_listings_status" CHECK (
        "status" IN ('draft', 'pending_review', 'approved', 'rejected', 'published', 'unlisted')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_listings_app_id" ON "public"."app_listings"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_listings_visibility" ON "public"."app_listings"("visibility");
CREATE INDEX IF NOT EXISTS "idx_app_listings_status" ON "public"."app_listings"("status");

COMMENT ON TABLE "public"."app_listings" IS '应用市场列表表';
COMMENT ON COLUMN "public"."app_listings"."listing_id" IS 'Listing ID';
COMMENT ON COLUMN "public"."app_listings"."visibility" IS '可见性 (private:私有:gray/public:公开:green)';
COMMENT ON COLUMN "public"."app_listings"."pricing_model" IS '定价模式 (free:免费:green/one_time:一次性付费:blue/subscription:订阅:orange/usage_based:按量计费:purple)';
COMMENT ON COLUMN "public"."app_listings"."status" IS '状态 (draft:草稿:gray/pending_review:待审核:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/unlisted:已下架:orange)';

-- ============================================================================
-- 表 5: app_installations - 安装记录表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_installations" (
    -- 主键
    "installation_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "owner_id" VARCHAR(255) NOT NULL,
    "app_id" VARCHAR(255) NOT NULL,
    "listing_id" UUID NOT NULL,

    -- 版本信息
    "installed_version" VARCHAR(50) NOT NULL,

    -- 权限
    "granted_scopes" JSONB NOT NULL DEFAULT '[]',

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 安装信息
    "installed_at" TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_used_at" TIMESTAMP,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_installations_installation_id_format" CHECK (
        "installation_id" ~ '^appi_[a-z0-9_-]+$'
    ),
    CONSTRAINT "chk_app_installations_status" CHECK (
        "status" IN ('active', 'update_available', 'pending_reauth', 'suspended', 'revoked')
    )
);

CREATE INDEX IF NOT EXISTS "idx_app_installations_owner_id" ON "public"."app_installations"("owner_id");
CREATE INDEX IF NOT EXISTS "idx_app_installations_app_id" ON "public"."app_installations"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_installations_status" ON "public"."app_installations"("status");

COMMENT ON TABLE "public"."app_installations" IS 'App 安装记录表';
COMMENT ON COLUMN "public"."app_installations"."installation_id" IS 'Installation ID';
COMMENT ON COLUMN "public"."app_installations"."owner_id" IS 'Owner ID';
COMMENT ON COLUMN "public"."app_installations"."granted_scopes" IS '授予的权限列表（JSONB）';
COMMENT ON COLUMN "public"."app_installations"."status" IS '状态 (active:活跃:green/update_available:有更新:blue/pending_reauth:待重新授权:orange/suspended:已暂停:red/revoked:已撤销:red)';

-- ============================================================================
-- 表 6: app_tools - Tool 定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_tools" (
    -- 主键
    "tool_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 基本信息
    "tool_name" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,

    -- Schema
    "input_schema" JSONB NOT NULL,
    "output_schema" JSONB NOT NULL,

    -- 可见性
    "visibility" VARCHAR(50) NOT NULL DEFAULT 'private',

    -- 风险等级
    "risk_level" VARCHAR(50) NOT NULL DEFAULT 'low',

    -- 所需权限
    "required_scopes" JSONB NOT NULL DEFAULT '[]',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_tools_tool_id_format" CHECK (
        "tool_id" ~ '^app_[a-z0-9_]+\.[a-z0-9_]+$'
    ),
    CONSTRAINT "chk_app_tools_visibility" CHECK (
        "visibility" IN ('private', 'public_service')
    ),
    CONSTRAINT "chk_app_tools_risk_level" CHECK (
        "risk_level" IN ('low', 'medium', 'high')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_tools_app_tool_name" ON "public"."app_tools"("app_id", "tool_name");
CREATE INDEX IF NOT EXISTS "idx_app_tools_app_id" ON "public"."app_tools"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_tools_visibility" ON "public"."app_tools"("visibility");

COMMENT ON TABLE "public"."app_tools" IS 'App Tool 定义表';
COMMENT ON COLUMN "public"."app_tools"."tool_id" IS 'Tool ID';
COMMENT ON COLUMN "public"."app_tools"."visibility" IS '可见性 (private:私有:gray/public_service:公开服务:green)';
COMMENT ON COLUMN "public"."app_tools"."risk_level" IS '风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)';

-- ============================================================================
-- 表 7: app_resources - Resource 定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_resources" (
    -- 主键
    "resource_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 基本信息
    "resource_name" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,

    -- Schema
    "schema_json" JSONB NOT NULL,

    -- 存储策略
    "storage_strategy" VARCHAR(50) NOT NULL DEFAULT 'jsonb',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_resources_resource_id_format" CHECK (
        "resource_id" ~ '^app_[a-z0-9_]+\.[a-z0-9_]+$'
    ),
    CONSTRAINT "chk_app_resources_storage_strategy" CHECK (
        "storage_strategy" IN ('jsonb', 'dedicated_table')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_resources_app_resource_name" ON "public"."app_resources"("app_id", "resource_name");
CREATE INDEX IF NOT EXISTS "idx_app_resources_app_id" ON "public"."app_resources"("app_id");

COMMENT ON TABLE "public"."app_resources" IS 'App Resource 定义表';
COMMENT ON COLUMN "public"."app_resources"."resource_id" IS 'Resource ID';
COMMENT ON COLUMN "public"."app_resources"."storage_strategy" IS '存储策略 (jsonb:JSONB存储:blue/dedicated_table:独立表:green)';

-- ============================================================================
-- 表 8: app_events - Event 定义表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_events" (
    -- 主键
    "event_id" VARCHAR(255) PRIMARY KEY,

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 基本信息
    "event_type" VARCHAR(100) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,

    -- Schema
    "payload_schema" JSONB NOT NULL,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_events_event_id_format" CHECK (
        "event_id" ~ '^app_[a-z0-9_]+\.[a-z0-9_]+$'
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_events_app_event_type" ON "public"."app_events"("app_id", "event_type");
CREATE INDEX IF NOT EXISTS "idx_app_events_app_id" ON "public"."app_events"("app_id");

COMMENT ON TABLE "public"."app_events" IS 'App Event 定义表';
COMMENT ON COLUMN "public"."app_events"."event_id" IS 'Event ID';

-- ============================================================================
-- 表 9: app_reviews - 审核记录表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_reviews" (
    -- 主键
    "review_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,
    "version_id" UUID NOT NULL,

    -- 审核信息
    "review_type" VARCHAR(50) NOT NULL,
    "reviewer_id" VARCHAR(255) NOT NULL,
    "review_status" VARCHAR(50) NOT NULL,
    "review_notes" TEXT,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_reviews_review_type" CHECK (
        "review_type" IN ('content', 'security', 'ui', 'frontend')
    ),
    CONSTRAINT "chk_app_reviews_review_status" CHECK (
        "review_status" IN ('pending', 'approved', 'rejected', 'changes_requested')
    )
);

CREATE INDEX IF NOT EXISTS "idx_app_reviews_app_id" ON "public"."app_reviews"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_reviews_version_id" ON "public"."app_reviews"("version_id");
CREATE INDEX IF NOT EXISTS "idx_app_reviews_review_status" ON "public"."app_reviews"("review_status");

COMMENT ON TABLE "public"."app_reviews" IS 'App 审核记录表';
COMMENT ON COLUMN "public"."app_reviews"."review_id" IS '审核 ID';
COMMENT ON COLUMN "public"."app_reviews"."review_type" IS '审核类型 (content:内容审核:blue/security:安全审核:red/ui:UI审核:green/frontend:前端审核:purple)';
COMMENT ON COLUMN "public"."app_reviews"."review_status" IS '审核状态 (pending:待审核:blue/approved:已批准:green/rejected:已拒绝:red/changes_requested:需要修改:orange)';

-- ============================================================================
-- 表 10: app_entitlements - 购买凭证表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_entitlements" (
    -- 主键
    "entitlement_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "owner_id" VARCHAR(255) NOT NULL,
    "listing_id" UUID NOT NULL,
    "installation_id" VARCHAR(255),

    -- 定价信息
    "pricing_model" VARCHAR(50) NOT NULL,
    "amount_paid" DECIMAL(10, 2),

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 购买信息
    "purchased_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMP,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_entitlements_pricing_model" CHECK (
        "pricing_model" IN ('free', 'one_time', 'subscription', 'usage_based')
    ),
    CONSTRAINT "chk_app_entitlements_status" CHECK (
        "status" IN ('active', 'expired', 'cancelled', 'refunded', 'suspended')
    )
);

CREATE INDEX IF NOT EXISTS "idx_app_entitlements_owner_id" ON "public"."app_entitlements"("owner_id");
CREATE INDEX IF NOT EXISTS "idx_app_entitlements_listing_id" ON "public"."app_entitlements"("listing_id");
CREATE INDEX IF NOT EXISTS "idx_app_entitlements_status" ON "public"."app_entitlements"("status");

COMMENT ON TABLE "public"."app_entitlements" IS 'App 购买凭证表';
COMMENT ON COLUMN "public"."app_entitlements"."entitlement_id" IS '凭证 ID';
COMMENT ON COLUMN "public"."app_entitlements"."pricing_model" IS '定价模式 (free:免费:green/one_time:一次性:blue/subscription:订阅:orange/usage_based:按量:purple)';
COMMENT ON COLUMN "public"."app_entitlements"."status" IS '状态 (active:活跃:green/expired:已过期:gray/cancelled:已取消:orange/refunded:已退款:red/suspended:已暂停:red)';

-- ============================================================================
-- 表 11: app_agent_bindings - Agent 绑定表
-- ============================================================================

CREATE TABLE IF NOT EXISTS "public"."app_agent_bindings" (
    -- 主键
    "binding_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "installation_id" VARCHAR(255) NOT NULL,
    "agent_id" VARCHAR(255) NOT NULL,

    -- 绑定信息
    "bound_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "bound_by" VARCHAR(255) NOT NULL,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_agent_bindings_status" CHECK (
        "status" IN ('active', 'revoked')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_agent_bindings_installation_agent"
    ON "public"."app_agent_bindings"("installation_id", "agent_id")
    WHERE "status" = 'active';
CREATE INDEX IF NOT EXISTS "idx_app_agent_bindings_installation_id" ON "public"."app_agent_bindings"("installation_id");
CREATE INDEX IF NOT EXISTS "idx_app_agent_bindings_agent_id" ON "public"."app_agent_bindings"("agent_id");

COMMENT ON TABLE "public"."app_agent_bindings" IS 'Installation 绑定的 Agent 列表';
COMMENT ON COLUMN "public"."app_agent_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "public"."app_agent_bindings"."status" IS '状态 (active:生效:green/revoked:已撤销:red)';
