-- =====================================================
-- HASN Agent 能力声明表
-- 对应协议: Layer 4 §1.2 Capability 声明
-- 每个 Agent MUST 在注册时声明其能力列表
-- =====================================================
CREATE TABLE "public"."hasn_agent_capabilities" (
  "id"                  bigserial PRIMARY KEY,
  "agent_hasn_id"       varchar(40) NOT NULL,
  "capability_id"       varchar(100) NOT NULL,
  "name"                varchar(100) NOT NULL,
  "description"         text,
  "input_schema"        jsonb NOT NULL DEFAULT '{}',
  "output_schema"       jsonb NOT NULL DEFAULT '{}',
  "requires_permission" jsonb NOT NULL DEFAULT '{}',
  "tags"                text[],
  "estimated_time_ms"   int4 NOT NULL DEFAULT 5000,
  "idempotent"          boolean NOT NULL DEFAULT false,
  "status"              varchar(20) NOT NULL DEFAULT 'active',
  "created_time"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"        timestamptz(6),
  CONSTRAINT "uq_hasn_agent_capability" UNIQUE ("agent_hasn_id", "capability_id")
);

CREATE INDEX "idx_capability_agent" ON "public"."hasn_agent_capabilities" ("agent_hasn_id");
CREATE INDEX "idx_capability_tags" ON "public"."hasn_agent_capabilities" USING GIN ("tags");
CREATE INDEX "idx_capability_status" ON "public"."hasn_agent_capabilities" ("status");

COMMENT ON TABLE "public"."hasn_agent_capabilities" IS 'HASN Agent 能力声明表';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."agent_hasn_id" IS 'Agent 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."capability_id" IS '能力唯一标识';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."name" IS '能力名称';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."description" IS '能力描述';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."input_schema" IS '输入 JSON Schema';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."output_schema" IS '输出 JSON Schema';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."requires_permission" IS '所需权限（JSONB: relation_types/min_trust_level/scopes）';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."tags" IS '能力标签';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."estimated_time_ms" IS '预计耗时（毫秒）';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."idempotent" IS '是否幂等';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."status" IS '状态 (active:启用:green/disabled:已禁用:orange)';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_agent_capabilities"."updated_time" IS '更新时间';
