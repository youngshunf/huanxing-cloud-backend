-- =====================================================
-- HASN 联系人关系表 (三维权限矩阵: relation_type × trust_level × scope)
-- =====================================================
CREATE TABLE "public"."hasn_contacts" (
  "id"                  bigserial PRIMARY KEY,
  "owner_id"            varchar(36) NOT NULL,
  "peer_id"             varchar(36) NOT NULL,
  "peer_owner_id"       varchar(36),
  "peer_type"           varchar(10) NOT NULL,
  "relation_type"       varchar(20) NOT NULL DEFAULT 'social',
  "trust_level"         smallint NOT NULL DEFAULT 1,
  "scope"               jsonb,
  "custom_permissions"  jsonb NOT NULL DEFAULT '{}',
  "nickname"            varchar(100),
  "tags"                text[],
  "subscription"        boolean NOT NULL DEFAULT false,
  "source_channel_binding_id" uuid,
  "channel_source"      varchar(30),
  "add_source"          varchar(20),
  "relation_revision"   bigint NOT NULL DEFAULT 1,
  "sync_revision"       bigint NOT NULL DEFAULT 1,
  "status"              varchar(20) NOT NULL DEFAULT 'pending',
  "request_message"     text,
  "auto_expire"         timestamptz(6),
  "connected_at"        timestamptz(6),
  "last_interaction_at" timestamptz(6),
  "interaction_count"   int4 NOT NULL DEFAULT 0,
  "created_time"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"        timestamptz(6),
  CONSTRAINT "uq_hasn_contact_relation" UNIQUE ("owner_id", "peer_id", "relation_type")
);

CREATE INDEX "idx_contact_owner" ON "public"."hasn_contacts" ("owner_id");
CREATE INDEX "idx_contact_peer" ON "public"."hasn_contacts" ("peer_id");
CREATE INDEX "idx_contact_type" ON "public"."hasn_contacts" ("owner_id", "relation_type");
CREATE INDEX "idx_contact_level" ON "public"."hasn_contacts" ("owner_id", "relation_type", "trust_level");
CREATE INDEX "idx_contact_status" ON "public"."hasn_contacts" ("status");
CREATE INDEX "idx_contact_expire" ON "public"."hasn_contacts" ("auto_expire") WHERE auto_expire IS NOT NULL;
CREATE INDEX "idx_contact_subscription" ON "public"."hasn_contacts" ("owner_id") WHERE subscription = true;
CREATE INDEX "idx_contact_peer_owner" ON "public"."hasn_contacts" ("peer_owner_id") WHERE peer_owner_id IS NOT NULL;
CREATE INDEX "idx_contact_channel_binding" ON "public"."hasn_contacts" ("source_channel_binding_id") WHERE "source_channel_binding_id" IS NOT NULL;
CREATE INDEX "idx_contact_sync_revision" ON "public"."hasn_contacts" ("sync_revision");

COMMENT ON TABLE "public"."hasn_contacts" IS 'HASN 联系人关系表';
COMMENT ON COLUMN "public"."hasn_contacts"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_contacts"."owner_id" IS '关系拥有者 hasn_id';
COMMENT ON COLUMN "public"."hasn_contacts"."peer_id" IS '对方 hasn_id';
COMMENT ON COLUMN "public"."hasn_contacts"."peer_owner_id" IS '对方归属人 hasn_id (peer 自己的 owner，区分"我的 agent"vs"别人的 agent")';
COMMENT ON COLUMN "public"."hasn_contacts"."peer_type" IS '对方类型 (human:人类:blue/agent:代理:green)';
COMMENT ON COLUMN "public"."hasn_contacts"."relation_type" IS '关系类型 (social:社交:blue/commerce:商业:orange/service:履约:green/professional:专业:purple/platform:平台:cyan)';
COMMENT ON COLUMN "public"."hasn_contacts"."trust_level" IS '信任等级 (0:已拉黑:red/1:陌生人:gray/2:普通联系人:blue/3:朋友:green/4:高信任:orange/5:所有者:purple)';
COMMENT ON COLUMN "public"."hasn_contacts"."scope" IS '关系作用域 (JSONB)';
COMMENT ON COLUMN "public"."hasn_contacts"."custom_permissions" IS '自定义权限覆盖 (JSONB)';
COMMENT ON COLUMN "public"."hasn_contacts"."nickname" IS '备注名';
COMMENT ON COLUMN "public"."hasn_contacts"."tags" IS '分组标签';
COMMENT ON COLUMN "public"."hasn_contacts"."subscription" IS '是否订阅推送';
COMMENT ON COLUMN "public"."hasn_contacts"."source_channel_binding_id" IS '来源 Channel Binding ID（第三方渠道反向 onboarding 关联）';
COMMENT ON COLUMN "public"."hasn_contacts"."channel_source" IS '来源渠道类型 (wechat:微信:green/feishu:飞书:blue/qq:QQ:cyan/webhook:Webhook:purple/manual:好友请求:gray/system:AI分身:orange)';
COMMENT ON COLUMN "public"."hasn_contacts"."add_source" IS '添加来源 (search_star_id:搜索唤星号:blue/search_nickname:搜索昵称:cyan/search_phone:手机号搜索:green/community:社区:purple/agent_discovery:Agent发现:orange/qr_code:扫一扫:gold/system:系统:gray/other:其他:default)';
COMMENT ON COLUMN "public"."hasn_contacts"."relation_revision" IS '关系修订号（权限矩阵变化时递增）';
COMMENT ON COLUMN "public"."hasn_contacts"."sync_revision" IS '服务端同步修订号';
COMMENT ON COLUMN "public"."hasn_contacts"."status" IS '状态 (pending:待处理:blue/connected:已连接:green/blocked:已拉黑:red/archived:已归档:gray)';
COMMENT ON COLUMN "public"."hasn_contacts"."request_message" IS '好友请求附言';
COMMENT ON COLUMN "public"."hasn_contacts"."auto_expire" IS '自动过期时间';
COMMENT ON COLUMN "public"."hasn_contacts"."connected_at" IS '建立连接时间';
COMMENT ON COLUMN "public"."hasn_contacts"."last_interaction_at" IS '最后互动时间';
COMMENT ON COLUMN "public"."hasn_contacts"."interaction_count" IS '互动次数';
COMMENT ON COLUMN "public"."hasn_contacts"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_contacts"."updated_time" IS '更新时间';
