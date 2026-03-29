-- =====================================================
-- HASN 客户端设备表 (记录所有注册的客户端设备)
-- 注意：hasn_agents 表有外键引用此表，必须先建此表
-- =====================================================
CREATE TABLE "public"."hasn_clients" (
  "id"           bigserial PRIMARY KEY,
  "client_id"    varchar(40) NOT NULL,
  "user_hasn_id" varchar(40) NOT NULL,
  "client_type"  varchar(20) NOT NULL DEFAULT 'desktop',
  "device_name"  varchar(100),
  "device_info"  jsonb NOT NULL DEFAULT '{}',
  "last_seen_at" timestamptz(6),
  "status"       varchar(20) NOT NULL DEFAULT 'active',
  "created_time" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time" timestamptz(6),
  UNIQUE("client_id")
);

CREATE INDEX "idx_hasn_clients_user" ON "public"."hasn_clients" ("user_hasn_id");
CREATE INDEX "idx_hasn_clients_status" ON "public"."hasn_clients" ("status");

COMMENT ON TABLE "public"."hasn_clients" IS 'HASN 客户端设备表';
COMMENT ON COLUMN "public"."hasn_clients"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_clients"."client_id" IS '客户端唯一标识 (格式: c_{uuid_short})';
COMMENT ON COLUMN "public"."hasn_clients"."user_hasn_id" IS '所属 Human 的 hasn_id（格式: h_xxx）';
COMMENT ON COLUMN "public"."hasn_clients"."client_type" IS '客户端类型 (desktop:桌面端:blue/mobile:手机端:green/web:网页端:orange/cloud:云端:purple)';
COMMENT ON COLUMN "public"."hasn_clients"."device_name" IS '设备名称';
COMMENT ON COLUMN "public"."hasn_clients"."device_info" IS '设备信息 (JSONB)';
COMMENT ON COLUMN "public"."hasn_clients"."last_seen_at" IS '最后活跃时间';
COMMENT ON COLUMN "public"."hasn_clients"."status" IS '状态 (active:活跃:green/disabled:已禁用:orange/deleted:已删除:red)';
COMMENT ON COLUMN "public"."hasn_clients"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_clients"."updated_time" IS '更新时间';
