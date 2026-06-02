-- =====================================================
-- HASN 好友请求表（请求生命周期与 hasn_contacts 关系生命周期解耦）
-- 设计依据 decisions/engineering/2026-05-30-contact-requests-table-split.md 第三节
-- 核心 hasn_contacts 只存已建立关系，请求落本表，通过才落 hasn_contacts
-- =====================================================
CREATE TABLE "public"."hasn_contact_requests" (
  "id"                    bigserial PRIMARY KEY,
  "from_id"               varchar(36) NOT NULL,
  "from_type"             varchar(10) NOT NULL DEFAULT 'human',
  "to_id"                 varchar(36) NOT NULL,
  "to_type"               varchar(10) NOT NULL DEFAULT 'human',
  "to_owner_id"           varchar(36) NOT NULL,
  "relation_type"         varchar(20) NOT NULL DEFAULT 'social',
  "requested_trust_level" smallint NOT NULL DEFAULT 2,
  "message"               text,
  "status"                varchar(20) NOT NULL DEFAULT 'pending',
  "decided_by"            varchar(36),
  "decided_at"            timestamptz(6),
  "resulting_contact_id"  bigint,
  "channel_source"        varchar(30),
  "created_time"          timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"          timestamptz(6)
);

-- 收到的待处理（审批人视角）
CREATE INDEX "idx_contact_request_to_owner_status" ON "public"."hasn_contact_requests" ("to_owner_id", "status");
-- 自己发出的（发起方视角）
CREATE INDEX "idx_contact_request_from_status" ON "public"."hasn_contact_requests" ("from_id", "status");
-- 目标维度
CREATE INDEX "idx_contact_request_to" ON "public"."hasn_contact_requests" ("to_id");
-- 部分唯一索引 同一对 from-to-relation 最多一条 pending，rejected/withdrawn/expired 不挡重新申请，根治拒绝后死锁
CREATE UNIQUE INDEX "uq_contact_request_pending" ON "public"."hasn_contact_requests" ("from_id", "to_id", "relation_type") WHERE "status" = 'pending';

COMMENT ON TABLE "public"."hasn_contact_requests" IS 'HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）';
COMMENT ON COLUMN "public"."hasn_contact_requests"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_contact_requests"."from_id" IS '发起方 hasn_id（恒 human）';
COMMENT ON COLUMN "public"."hasn_contact_requests"."from_type" IS '发起方类型 (human:人类:blue/agent:代理:green)';
COMMENT ON COLUMN "public"."hasn_contact_requests"."to_id" IS '目标 hasn_id（解析后恒 human）';
COMMENT ON COLUMN "public"."hasn_contact_requests"."to_type" IS '目标类型 (human:人类:blue/agent:代理:green)';
COMMENT ON COLUMN "public"."hasn_contact_requests"."to_owner_id" IS '审批人 hasn_id（=目标本人，agent 目标则解析为其主人）';
COMMENT ON COLUMN "public"."hasn_contact_requests"."relation_type" IS '关系类型 (social:社交:blue/commerce:商业:orange/service:履约:green/professional:专业:purple/platform:平台:cyan)';
COMMENT ON COLUMN "public"."hasn_contact_requests"."requested_trust_level" IS '请求授予的信任等级（通过时落到 hasn_contacts.trust_level）';
COMMENT ON COLUMN "public"."hasn_contact_requests"."message" IS '请求附言';
COMMENT ON COLUMN "public"."hasn_contact_requests"."status" IS '状态 (pending:待处理:blue/accepted:已通过:green/rejected:已拒绝:red/withdrawn:已撤回:gray/expired:已过期:gray)';
COMMENT ON COLUMN "public"."hasn_contact_requests"."decided_by" IS '回应人 hasn_id';
COMMENT ON COLUMN "public"."hasn_contact_requests"."decided_at" IS '回应时间';
COMMENT ON COLUMN "public"."hasn_contact_requests"."resulting_contact_id" IS '通过后建立的 hasn_contacts 行 ID（审计链）';
COMMENT ON COLUMN "public"."hasn_contact_requests"."channel_source" IS '来源渠道类型 (wechat:微信:green/feishu:飞书:blue/qq:QQ:cyan/webhook:Webhook:purple/manual:好友请求:gray/system:系统:orange)';
COMMENT ON COLUMN "public"."hasn_contact_requests"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_contact_requests"."updated_time" IS '更新时间';
