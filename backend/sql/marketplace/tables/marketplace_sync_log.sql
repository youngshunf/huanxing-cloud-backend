-- 技能市场同步日志表
CREATE TABLE "public"."marketplace_sync_log" (
  "id" bigserial PRIMARY KEY,
  "sync_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "source" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'running',
  "total_count" int4 NOT NULL DEFAULT 0,
  "success_count" int4 NOT NULL DEFAULT 0,
  "failed_count" int4 NOT NULL DEFAULT 0,
  "error_message" text COLLATE "pg_catalog"."default",
  "started_at" timestamptz(6) NOT NULL DEFAULT NOW(),
  "completed_at" timestamptz(6),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6)
);

CREATE INDEX "idx_marketplace_sync_log_sync_type" ON "public"."marketplace_sync_log" ("sync_type");
CREATE INDEX "idx_marketplace_sync_log_source" ON "public"."marketplace_sync_log" ("source");
CREATE INDEX "idx_marketplace_sync_log_status" ON "public"."marketplace_sync_log" ("status");
CREATE INDEX "idx_marketplace_sync_log_started_at" ON "public"."marketplace_sync_log" ("started_at" DESC);

COMMENT ON COLUMN "public"."marketplace_sync_log"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."marketplace_sync_log"."sync_type" IS '同步类型 (skill:技能:blue/template:模板:cyan/full:全量:purple)';
COMMENT ON COLUMN "public"."marketplace_sync_log"."source" IS '同步来源 (github:GitHub:blue/clawhub:ClawHub:green/webhook:Webhook:purple/manual:手动:gray)';
COMMENT ON COLUMN "public"."marketplace_sync_log"."status" IS '同步状态 (running:运行中:blue/success:成功:green/failed:失败:red/partial:部分成功:orange)';
COMMENT ON COLUMN "public"."marketplace_sync_log"."total_count" IS '总数量';
COMMENT ON COLUMN "public"."marketplace_sync_log"."success_count" IS '成功数量';
COMMENT ON COLUMN "public"."marketplace_sync_log"."failed_count" IS '失败数量';
COMMENT ON COLUMN "public"."marketplace_sync_log"."error_message" IS '错误信息';
COMMENT ON COLUMN "public"."marketplace_sync_log"."started_at" IS '开始时间';
COMMENT ON COLUMN "public"."marketplace_sync_log"."completed_at" IS '完成时间';
COMMENT ON TABLE "public"."marketplace_sync_log" IS '技能市场同步日志表';
