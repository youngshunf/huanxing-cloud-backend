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
