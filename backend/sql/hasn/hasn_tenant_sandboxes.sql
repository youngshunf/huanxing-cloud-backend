-- =====================================================
-- HASN Tenant Sandbox lifecycle 表（S1/S3 codegen 输入）
-- =====================================================
CREATE TABLE "public"."hasn_tenant_sandboxes" (
  "id"              bigserial PRIMARY KEY,
  "sandbox_id"      varchar(40) NOT NULL,
  "owner_id"        varchar(40) NOT NULL,
  "node_id"         varchar(40),
  "image_tier"      varchar(30) NOT NULL DEFAULT 'cloud-lite',
  "state"           varchar(20) NOT NULL DEFAULT 'sleeping',
  "router_base_url" varchar(300),
  "resource_profile" jsonb NOT NULL DEFAULT '{}',
  "last_health_json" jsonb NOT NULL DEFAULT '{}',
  "created_at_remote" timestamptz(6),
  "woke_at"         timestamptz(6),
  "slept_at"        timestamptz(6),
  "deleted_at"      timestamptz(6),
  "purge_after"     timestamptz(6),
  "created_time"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"    timestamptz(6),
  CONSTRAINT "uq_hasn_tenant_sandboxes_sandbox" UNIQUE ("sandbox_id"),
  CONSTRAINT "uq_hasn_tenant_sandboxes_owner" UNIQUE ("owner_id")
);

CREATE INDEX "idx_hasn_tenant_sandboxes_owner_state" ON "public"."hasn_tenant_sandboxes" ("owner_id", "state");
CREATE INDEX "idx_hasn_tenant_sandboxes_node" ON "public"."hasn_tenant_sandboxes" ("node_id") WHERE "node_id" IS NOT NULL;
CREATE INDEX "idx_hasn_tenant_sandboxes_purge" ON "public"."hasn_tenant_sandboxes" ("purge_after") WHERE "purge_after" IS NOT NULL;

COMMENT ON TABLE "public"."hasn_tenant_sandboxes" IS 'HASN Tenant Sandbox lifecycle 表';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."sandbox_id" IS 'Sandbox 唯一 ID (sb_{uuid})';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."owner_id" IS 'Owner hasn_id';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."node_id" IS '关联 cloud Node ID（可空）';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."image_tier" IS '镜像层级 (cloud-lite:轻量:green/cloud-cli:CLI增强:blue)';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."state" IS '状态 (active:运行中:green/sleeping:休眠:blue/deleted:已删除:gray/error:异常:red)';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."router_base_url" IS 'Tenant Router 公开 base URL；不得保存本地 endpoint/PID';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."resource_profile" IS '资源配额摘要 JSON';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."last_health_json" IS '最近健康摘要 JSON';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."created_at_remote" IS '底层 sandbox 创建时间';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."woke_at" IS '最近唤醒时间';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."slept_at" IS '最近休眠时间';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."deleted_at" IS '删除标记时间';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."purge_after" IS '可物理清理时间（删除后 ETA 24h）';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_tenant_sandboxes"."updated_time" IS '更新时间';
