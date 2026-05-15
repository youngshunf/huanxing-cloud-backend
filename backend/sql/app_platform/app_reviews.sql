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
