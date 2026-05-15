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
