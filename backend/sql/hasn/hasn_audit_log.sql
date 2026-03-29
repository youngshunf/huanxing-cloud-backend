-- =====================================================
-- HASN 审计日志表
-- =====================================================
CREATE TABLE "public"."hasn_audit_log" (
  "id"           bigserial PRIMARY KEY,
  "actor_id"     varchar(36) NOT NULL,
  "actor_type"   varchar(10) NOT NULL,
  "action"       varchar(50) NOT NULL,
  "target_type"  varchar(20),
  "target_id"    varchar(36),
  "details"      jsonb NOT NULL DEFAULT '{}',
  "ip_address"   varchar(45),
  "created_time" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time" timestamptz(6)
);

CREATE INDEX "idx_audit_actor" ON "public"."hasn_audit_log" ("actor_id", "created_time");
CREATE INDEX "idx_audit_action" ON "public"."hasn_audit_log" ("action", "created_time");
CREATE INDEX "idx_audit_target" ON "public"."hasn_audit_log" ("target_type", "target_id");

COMMENT ON TABLE "public"."hasn_audit_log" IS 'HASN 审计日志表';
COMMENT ON COLUMN "public"."hasn_audit_log"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_audit_log"."actor_id" IS '操作者 hasn_id';
COMMENT ON COLUMN "public"."hasn_audit_log"."actor_type" IS '操作者类型 (human:人类:blue/agent:代理:green/system:系统:gray)';
COMMENT ON COLUMN "public"."hasn_audit_log"."action" IS '操作类型 (register:注册:blue/login:登录:green/send_message:发消息:cyan/add_contact:加好友:orange/block_contact:拉黑:red/create_agent:创建Agent:purple/delete_agent:删除Agent:red/bind_client:绑定客户端:green/unbind_client:解绑客户端:orange)';
COMMENT ON COLUMN "public"."hasn_audit_log"."target_type" IS '目标类型 (human:人类:blue/agent:代理:green/client:客户端:orange/conversation:会话:cyan/message:消息:purple)';
COMMENT ON COLUMN "public"."hasn_audit_log"."target_id" IS '目标 ID';
COMMENT ON COLUMN "public"."hasn_audit_log"."details" IS '操作详情 (JSONB)';
COMMENT ON COLUMN "public"."hasn_audit_log"."ip_address" IS 'IP 地址';
COMMENT ON COLUMN "public"."hasn_audit_log"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_audit_log"."updated_time" IS '更新时间';
