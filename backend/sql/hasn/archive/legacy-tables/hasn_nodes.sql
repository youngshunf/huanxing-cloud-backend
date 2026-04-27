-- HASN Node 主表
CREATE TABLE "public"."hasn_nodes" (
  "id"                   bigserial PRIMARY KEY,
  "node_id"              varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id"              bigint,
  "allowed_owner_hasn_ids" jsonb,
  "node_type"            varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'desktop',
  "node_name"            varchar(100) COLLATE "pg_catalog"."default",
  "device_fingerprint"   varchar(128) COLLATE "pg_catalog"."default",
  "device_platform"      varchar(32) COLLATE "pg_catalog"."default",
  "app_version"          varchar(32) COLLATE "pg_catalog"."default",
  "node_info"            jsonb NOT NULL DEFAULT '{}',
  "node_key_hash"        varchar(64) COLLATE "pg_catalog"."default",
  "capacity"             int4 NOT NULL DEFAULT 1,
  "created_by_owner_id"  varchar(40) COLLATE "pg_catalog"."default",
  "last_seen_at"         timestamptz(6),
  "status"               varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'active',
  "created_time"         timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time"         timestamptz(6),
  UNIQUE("node_id")
);

CREATE INDEX "idx_hasn_nodes_type" ON "public"."hasn_nodes" ("node_type");
CREATE INDEX "idx_hasn_nodes_status" ON "public"."hasn_nodes" ("status");
CREATE INDEX "idx_hasn_nodes_user_id" ON "public"."hasn_nodes" ("user_id");
CREATE INDEX "idx_hasn_nodes_creator" ON "public"."hasn_nodes" ("created_by_owner_id");
CREATE INDEX "idx_hasn_nodes_device_fingerprint" ON "public"."hasn_nodes" ("device_fingerprint");

COMMENT ON TABLE "public"."hasn_nodes" IS 'HASN Node 主表';
COMMENT ON COLUMN "public"."hasn_nodes"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_nodes"."node_id" IS '节点唯一标识 (格式: n_{uuid_short})';
COMMENT ON COLUMN "public"."hasn_nodes"."user_id" IS '平台用户 ID（桌面端/唤星账号场景）';
COMMENT ON COLUMN "public"."hasn_nodes"."allowed_owner_hasn_ids" IS '允许绑定的 Owner 列表 JSON（NULL/空数组表示不限制，SDK 场景可指定白名单）';
COMMENT ON COLUMN "public"."hasn_nodes"."node_type" IS '节点类型 (desktop:桌面端:blue/mobile:手机端:green/web:网页端:orange/cloud:云端:purple/sdk:SDK:cyan)';
COMMENT ON COLUMN "public"."hasn_nodes"."node_name" IS '节点名称';
COMMENT ON COLUMN "public"."hasn_nodes"."device_fingerprint" IS '设备指纹（用于幂等创建和识别同一设备）';
COMMENT ON COLUMN "public"."hasn_nodes"."device_platform" IS '设备平台 (macos:macOS:blue/windows:Windows:cyan/linux:Linux:green/ios:iOS:purple/android:Android:orange/web:Web:gray/sdk:SDK:yellow/server:Server:red)';
COMMENT ON COLUMN "public"."hasn_nodes"."app_version" IS '接入端应用版本';
COMMENT ON COLUMN "public"."hasn_nodes"."node_info" IS '节点信息 JSON';
COMMENT ON COLUMN "public"."hasn_nodes"."node_key_hash" IS 'Node Key 的 SHA256 哈希';
COMMENT ON COLUMN "public"."hasn_nodes"."capacity" IS '最大 Agent 承载量';
COMMENT ON COLUMN "public"."hasn_nodes"."created_by_owner_id" IS '初始创建 Owner（仅审计用途）';
COMMENT ON COLUMN "public"."hasn_nodes"."last_seen_at" IS '最后活跃时间';
COMMENT ON COLUMN "public"."hasn_nodes"."status" IS '状态 (active:活跃:green/disabled:已禁用:orange/deleted:已删除:red)';
COMMENT ON COLUMN "public"."hasn_nodes"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_nodes"."updated_time" IS '更新时间';
