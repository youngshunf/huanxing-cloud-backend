-- ============================================================================
-- AI-Native 应用平台 - 权限系统表
-- ============================================================================
-- 文件: 001_create_permission_tables.sql
-- 描述: 权限系统核心表（4 张）
-- 参考: docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/10-权限系统设计.md
--       docs/HASN-centralized/HASN-Protocol/Architecture/AI-Native应用平台/11-数据模型.md
-- 作者: 唤星项目
-- 日期: 2026-05-14
-- ============================================================================

-- ============================================================================
-- 表 1: platform_scopes - 平台权限定义表
-- ============================================================================
-- 描述: 平台级权限定义（hasn.* namespace）
-- 用途: 定义所有平台提供的核心权限，如 Agent 调用、IM 发送等

CREATE TABLE IF NOT EXISTS "public"."platform_scopes" (
    -- 主键
    "scope" VARCHAR(255) PRIMARY KEY,

    -- 基本信息
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "reason" TEXT,

    -- 分类
    "category" VARCHAR(50) NOT NULL,

    -- 风险等级
    "risk_level" VARCHAR(20) NOT NULL,

    -- 权限控制
    "requires_owner_confirmation" BOOLEAN DEFAULT FALSE,

    -- 限流配置
    "rate_limit_per_minute" INTEGER,
    "rate_limit_per_hour" INTEGER,
    "rate_limit_per_day" INTEGER,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_platform_scopes_scope_format" CHECK (
        "scope" ~ '^hasn\.[a-z_]+(\.[a-z_]+)+$'
    ),
    CONSTRAINT "chk_platform_scopes_category" CHECK (
        "category" IN ('agent', 'im', 'app', 'data', 'system')
    ),
    CONSTRAINT "chk_platform_scopes_risk_level" CHECK (
        "risk_level" IN ('low', 'medium', 'high')
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS "idx_platform_scopes_category" ON "public"."platform_scopes"("category");
CREATE INDEX IF NOT EXISTS "idx_platform_scopes_risk_level" ON "public"."platform_scopes"("risk_level");

-- 表注释
COMMENT ON TABLE "public"."platform_scopes" IS '平台权限定义表（hasn.* namespace）';

-- 字段注释
COMMENT ON COLUMN "public"."platform_scopes"."scope" IS '权限标识，格式：hasn.{category}.{resource}.{action}';
COMMENT ON COLUMN "public"."platform_scopes"."display_name" IS '权限显示名称';
COMMENT ON COLUMN "public"."platform_scopes"."description" IS '权限描述';
COMMENT ON COLUMN "public"."platform_scopes"."reason" IS '为什么需要这个权限';
COMMENT ON COLUMN "public"."platform_scopes"."category" IS '权限分类 (agent:Agent相关:blue/im:即时消息:green/app:应用相关:purple/data:数据相关:orange/system:系统相关:red)';
COMMENT ON COLUMN "public"."platform_scopes"."risk_level" IS '风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)';
COMMENT ON COLUMN "public"."platform_scopes"."requires_owner_confirmation" IS '是否需要 Owner 二次确认';
COMMENT ON COLUMN "public"."platform_scopes"."rate_limit_per_minute" IS '每分钟限流次数';
COMMENT ON COLUMN "public"."platform_scopes"."rate_limit_per_hour" IS '每小时限流次数';
COMMENT ON COLUMN "public"."platform_scopes"."rate_limit_per_day" IS '每天限流次数';
COMMENT ON COLUMN "public"."platform_scopes"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."platform_scopes"."updated_time" IS '更新时间';

-- 初始数据
INSERT INTO "public"."platform_scopes" ("scope", "display_name", "description", "reason", "category", "risk_level", "requires_owner_confirmation", "rate_limit_per_minute", "rate_limit_per_hour") VALUES
('hasn.agent.profile.read', '读取 Agent 基本信息', '允许读取 Agent 的名称、头像等基本信息', '用于展示 Agent 信息', 'agent', 'low', FALSE, NULL, NULL),
('hasn.agent.memory.read', '读取 Agent 记忆', '允许读取 Agent 的记忆内容', '用于分析和处理 Agent 记忆', 'agent', 'medium', FALSE, 100, 1000),
('hasn.agent.memory.write', '写入 Agent 记忆', '允许向 Agent 写入记忆', '用于记录重要信息', 'agent', 'high', TRUE, 10, 100),
('hasn.agent.invoke', '调用 Agent', '允许调用 Owner 授权的 Agent', '用于 App 调用 Agent 执行任务', 'agent', 'medium', FALSE, 10, 100),
('hasn.im.send', '发送即时消息', '允许向 Owner 或 Agent 发送消息', '用于通知和交互', 'im', 'medium', FALSE, 20, 200),
('hasn.im.receive', '接收即时消息', '允许接收发送给 App 的消息', '用于接收用户消息', 'im', 'medium', FALSE, NULL, NULL),
('hasn.im.read', '读取即时消息', '允许读取消息历史', '用于分析对话内容', 'im', 'high', TRUE, 100, 1000),
('hasn.app.event.emit', '发射业务事件', '允许 App 发射事件唤醒 Agent', '用于事件驱动的工作流', 'app', 'low', FALSE, 100, 1000),
('hasn.app.tool.call', '调用其他 App Tool', '允许调用其他 App 的 Tool', '用于 App 间协作', 'app', 'medium', FALSE, 100, 1000),
('hasn.app.tool.serve_public', '对外暴露公开服务', '允许 App 对外暴露公开服务', '用于提供公开 API', 'app', 'high', TRUE, NULL, NULL),
('hasn.app.trade.bridge', '推进交易履约', '允许 App 事件推进交易履约状态', '用于服务交易', 'app', 'high', TRUE, 10, 100)
ON CONFLICT ("scope") DO NOTHING;

-- ============================================================================
-- 表 2: app_scopes - 应用权限定义表
-- ============================================================================
-- 描述: 应用级权限定义（{domain}.* namespace）
-- 用途: 存储 App 在 Manifest 中声明的自定义权限

CREATE TABLE IF NOT EXISTS "public"."app_scopes" (
    -- 主键
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "app_id" VARCHAR(255) NOT NULL,

    -- 权限信息
    "scope" VARCHAR(255) NOT NULL,
    "display_name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "reason" TEXT,

    -- 风险等级
    "risk_level" VARCHAR(20) NOT NULL,

    -- 权限控制
    "requires_owner_confirmation" BOOLEAN DEFAULT FALSE,

    -- 限流配置
    "rate_limit_per_minute" INTEGER,
    "rate_limit_per_hour" INTEGER,
    "rate_limit_per_day" INTEGER,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_scopes_scope_format" CHECK (
        "scope" ~ '^[a-z0-9_]+\.[a-z_]+\.[a-z_]+$'
    ),
    CONSTRAINT "chk_app_scopes_risk_level" CHECK (
        "risk_level" IN ('low', 'medium', 'high')
    )
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_scopes_app_scope" ON "public"."app_scopes"("app_id", "scope");
CREATE INDEX IF NOT EXISTS "idx_app_scopes_app_id" ON "public"."app_scopes"("app_id");
CREATE INDEX IF NOT EXISTS "idx_app_scopes_risk_level" ON "public"."app_scopes"("risk_level");

-- 表注释
COMMENT ON TABLE "public"."app_scopes" IS '应用权限定义表（{domain}.* namespace）';

-- 字段注释
COMMENT ON COLUMN "public"."app_scopes"."id" IS '主键 UUID';
COMMENT ON COLUMN "public"."app_scopes"."app_id" IS '关联的 App ID';
COMMENT ON COLUMN "public"."app_scopes"."scope" IS '权限标识，格式：{domain}.{resource}.{action}';
COMMENT ON COLUMN "public"."app_scopes"."display_name" IS '权限显示名称';
COMMENT ON COLUMN "public"."app_scopes"."description" IS '权限描述';
COMMENT ON COLUMN "public"."app_scopes"."reason" IS '为什么需要这个权限';
COMMENT ON COLUMN "public"."app_scopes"."risk_level" IS '风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)';
COMMENT ON COLUMN "public"."app_scopes"."requires_owner_confirmation" IS '是否需要 Owner 二次确认';
COMMENT ON COLUMN "public"."app_scopes"."rate_limit_per_minute" IS '每分钟限流次数';
COMMENT ON COLUMN "public"."app_scopes"."rate_limit_per_hour" IS '每小时限流次数';
COMMENT ON COLUMN "public"."app_scopes"."rate_limit_per_day" IS '每天限流次数';
COMMENT ON COLUMN "public"."app_scopes"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."app_scopes"."updated_time" IS '更新时间';

-- ============================================================================
-- 表 3: app_permission_grants - 权限授予记录表
-- ============================================================================
-- 描述: Owner 授予 Installation 的权限记录
-- 用途: 记录每个 Installation 被授予的权限及其状态

CREATE TABLE IF NOT EXISTS "public"."app_permission_grants" (
    -- 主键
    "grant_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "installation_id" VARCHAR(255) NOT NULL,
    "scope" VARCHAR(255) NOT NULL,

    -- 授予信息
    "granted_by" VARCHAR(255) NOT NULL,
    "granted_at" TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "grant_source" VARCHAR(50) NOT NULL,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'active',

    -- 撤销信息
    "revoked_at" TIMESTAMP,
    "revoked_by" VARCHAR(255),
    "revocation_reason" TEXT,

    -- 使用统计
    "last_used_at" TIMESTAMP,
    "usage_count" INTEGER NOT NULL DEFAULT 0,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_permission_grants_grant_source" CHECK (
        "grant_source" IN ('installation', 'dynamic_request', 'version_upgrade')
    ),
    CONSTRAINT "chk_app_permission_grants_status" CHECK (
        "status" IN ('active', 'revoked')
    )
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS "idx_app_permission_grants_installation_scope"
    ON "public"."app_permission_grants"("installation_id", "scope")
    WHERE "status" = 'active';
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_installation_id" ON "public"."app_permission_grants"("installation_id");
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_scope" ON "public"."app_permission_grants"("scope");
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_status" ON "public"."app_permission_grants"("status");
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_granted_at" ON "public"."app_permission_grants"("granted_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_app_permission_grants_last_used_at" ON "public"."app_permission_grants"("last_used_at" DESC NULLS LAST);

-- 表注释
COMMENT ON TABLE "public"."app_permission_grants" IS '权限授予记录表';

-- 字段注释
COMMENT ON COLUMN "public"."app_permission_grants"."grant_id" IS '授权记录 ID';
COMMENT ON COLUMN "public"."app_permission_grants"."installation_id" IS '关联的 Installation ID';
COMMENT ON COLUMN "public"."app_permission_grants"."scope" IS '授予的权限标识';
COMMENT ON COLUMN "public"."app_permission_grants"."granted_by" IS '授予者 Owner ID';
COMMENT ON COLUMN "public"."app_permission_grants"."granted_at" IS '授予时间';
COMMENT ON COLUMN "public"."app_permission_grants"."grant_source" IS '授予来源 (installation:安装时:blue/dynamic_request:动态请求:green/version_upgrade:版本升级:orange)';
COMMENT ON COLUMN "public"."app_permission_grants"."status" IS '状态 (active:生效:green/revoked:已撤销:red)';
COMMENT ON COLUMN "public"."app_permission_grants"."revoked_at" IS '撤销时间';
COMMENT ON COLUMN "public"."app_permission_grants"."revoked_by" IS '撤销者（owner 或 platform）';
COMMENT ON COLUMN "public"."app_permission_grants"."revocation_reason" IS '撤销原因';
COMMENT ON COLUMN "public"."app_permission_grants"."last_used_at" IS '最后使用时间';
COMMENT ON COLUMN "public"."app_permission_grants"."usage_count" IS '使用次数';
COMMENT ON COLUMN "public"."app_permission_grants"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."app_permission_grants"."updated_time" IS '更新时间';

-- ============================================================================
-- 表 4: app_dynamic_permission_requests - 动态权限请求表
-- ============================================================================
-- 描述: App 运行时动态请求权限的记录
-- 用途: 记录 App 在运行时请求额外权限的请求及其处理状态

CREATE TABLE IF NOT EXISTS "public"."app_dynamic_permission_requests" (
    -- 主键
    "request_id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    "installation_id" VARCHAR(255) NOT NULL,
    "scope" VARCHAR(255) NOT NULL,

    -- 请求信息
    "requested_at" TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "request_reason" TEXT NOT NULL,
    "request_context" JSONB,

    -- 状态
    "status" VARCHAR(50) NOT NULL DEFAULT 'pending',

    -- 决策信息
    "decided_at" TIMESTAMP,
    "decided_by" VARCHAR(255),
    "decision_reason" TEXT,

    -- 过期时间
    "expires_at" TIMESTAMP WITH TIME ZONE WITH TIME ZONE WITH TIME ZONE NOT NULL,

    -- 审计字段
    "created_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP WITH TIME ZONE,

    -- 约束
    CONSTRAINT "chk_app_dynamic_permission_requests_status" CHECK (
        "status" IN ('pending', 'approved', 'denied', 'expired')
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS "idx_app_dynamic_permission_requests_installation_id"
    ON "public"."app_dynamic_permission_requests"("installation_id");
CREATE INDEX IF NOT EXISTS "idx_app_dynamic_permission_requests_status"
    ON "public"."app_dynamic_permission_requests"("status");
CREATE INDEX IF NOT EXISTS "idx_app_dynamic_permission_requests_requested_at"
    ON "public"."app_dynamic_permission_requests"("requested_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_app_dynamic_permission_requests_expires_at"
    ON "public"."app_dynamic_permission_requests"("expires_at");

-- 表注释
COMMENT ON TABLE "public"."app_dynamic_permission_requests" IS '动态权限请求表';

-- 字段注释
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."request_id" IS '请求 ID';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."installation_id" IS '关联的 Installation ID';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."scope" IS '请求的权限标识';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."requested_at" IS '请求时间';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."request_reason" IS 'App 说明为什么需要这个权限';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."request_context" IS '请求时的上下文信息（JSONB）';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."status" IS '状态 (pending:待处理:blue/approved:已批准:green/denied:已拒绝:red/expired:已过期:gray)';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."decided_at" IS '决策时间';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."decided_by" IS '决策者 Owner ID';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."decision_reason" IS '决策理由';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."expires_at" IS '请求过期时间（默认 24 小时）';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."updated_time" IS '更新时间';

-- ============================================================================
-- 完成
-- ============================================================================
