-- ============================================================================
-- 表 4: app_dynamic_permission_requests - 动态权限请求表
-- ============================================================================

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
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."request_context" IS '请求上下文（JSONB）';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."status" IS '状态 (pending:待处理:blue/approved:已批准:green/denied:已拒绝:red/expired:已过期:gray)';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."decided_at" IS '决策时间';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."decided_by" IS '决策者 Owner ID';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."decision_reason" IS '决策理由';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."expires_at" IS '请求过期时间';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."app_dynamic_permission_requests"."updated_time" IS '更新时间';
