-- ============================================================
-- 唤星云服务 - 数据库表设计
-- 数据库: PostgreSQL (creator_flow) | Schema: public
-- 日期: 2026-02-27
-- ============================================================

-- 1. 唤星服务器表
CREATE TABLE "public"."huanxing_server" (
    "id"              bigserial PRIMARY KEY,
    "server_id"       varchar(64) UNIQUE NOT NULL,
    "server_name"     varchar(128),
    "ip_address"      varchar(45) NOT NULL,
    "port"            integer DEFAULT 22,
    "region"          varchar(64),
    "provider"        varchar(64),
    "max_users"       integer DEFAULT 100,
    "status"          smallint DEFAULT 1,
    "gateway_status"  varchar(16) DEFAULT 'unknown',
    "last_heartbeat"  timestamp,
    "config"          jsonb,
    "remark"          varchar(512),
    "created_time"    timestamp DEFAULT now(),
    "updated_time"    timestamp
);

COMMENT ON TABLE "public"."huanxing_server" IS '唤星服务器表';
COMMENT ON COLUMN "public"."huanxing_server"."id" IS '主键ID';
COMMENT ON COLUMN "public"."huanxing_server"."server_id" IS '服务器唯一标识（如 server-001）';
COMMENT ON COLUMN "public"."huanxing_server"."server_name" IS '服务器名称（如 京东云-华北1）';
COMMENT ON COLUMN "public"."huanxing_server"."ip_address" IS '服务器IP地址';
COMMENT ON COLUMN "public"."huanxing_server"."port" IS 'SSH端口';
COMMENT ON COLUMN "public"."huanxing_server"."region" IS '地域（如 cn-north-1）';
COMMENT ON COLUMN "public"."huanxing_server"."provider" IS '云服务商（如 jdcloud/aliyun/tencent）';
COMMENT ON COLUMN "public"."huanxing_server"."max_users" IS '最大用户容量';
COMMENT ON COLUMN "public"."huanxing_server"."status" IS '状态：1-启用 0-禁用';
COMMENT ON COLUMN "public"."huanxing_server"."gateway_status" IS 'Gateway状态: running/stopped/unknown';
COMMENT ON COLUMN "public"."huanxing_server"."last_heartbeat" IS '最后心跳时间';
COMMENT ON COLUMN "public"."huanxing_server"."config" IS '服务器配置信息（JSON）';
COMMENT ON COLUMN "public"."huanxing_server"."remark" IS '备注';
COMMENT ON COLUMN "public"."huanxing_server"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."huanxing_server"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_server_status" ON "public"."huanxing_server"("status");

-- 2. 唤星用户表
CREATE TABLE "public"."huanxing_user" (
    "id"              bigserial PRIMARY KEY,
    "user_id"         bigint NOT NULL,
    "server_id"       varchar(64) NOT NULL,
    "agent_id"        varchar(128) UNIQUE,
    "star_name"       varchar(64),
    "template"        varchar(64) NOT NULL,
    "workspace_path"  varchar(256),
    "agent_status"    smallint DEFAULT 1,
    "channel_type"    varchar(16),
    "channel_peer_id" varchar(128),
    "remark"          varchar(512),
    "created_time"    timestamp DEFAULT now(),
    "updated_time"    timestamp,
    UNIQUE("user_id", "server_id")
);

COMMENT ON TABLE "public"."huanxing_user" IS '唤星用户表';
COMMENT ON COLUMN "public"."huanxing_user"."id" IS '主键ID';
COMMENT ON COLUMN "public"."huanxing_user"."user_id" IS '关联 sys_user.id';
COMMENT ON COLUMN "public"."huanxing_user"."server_id" IS '所在服务器ID';
COMMENT ON COLUMN "public"."huanxing_user"."agent_id" IS 'Agent ID（如 user-abc123）';
COMMENT ON COLUMN "public"."huanxing_user"."star_name" IS '分身名字';
COMMENT ON COLUMN "public"."huanxing_user"."template" IS '模板类型：media-creator/side-hustle/finance/office/health/assistant';
COMMENT ON COLUMN "public"."huanxing_user"."workspace_path" IS '工作区路径';
COMMENT ON COLUMN "public"."huanxing_user"."agent_status" IS 'Agent状态：1-启用 0-禁用';
COMMENT ON COLUMN "public"."huanxing_user"."channel_type" IS '注册渠道：feishu/qq/wechat';
COMMENT ON COLUMN "public"."huanxing_user"."channel_peer_id" IS '渠道用户ID';
COMMENT ON COLUMN "public"."huanxing_user"."remark" IS '备注';
COMMENT ON COLUMN "public"."huanxing_user"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."huanxing_user"."updated_time" IS '更新时间';

CREATE INDEX "idx_hx_user_server" ON "public"."huanxing_user"("server_id");
CREATE INDEX "idx_hx_user_user" ON "public"."huanxing_user"("user_id");
CREATE INDEX "idx_hx_user_channel" ON "public"."huanxing_user"("channel_type", "channel_peer_id");
CREATE INDEX "idx_hx_user_status" ON "public"."huanxing_user"("agent_status");
