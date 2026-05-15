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
