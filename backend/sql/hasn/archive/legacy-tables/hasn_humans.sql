CREATE TABLE "public"."hasn_humans" (
    "id"              bigserial PRIMARY KEY,
    "hasn_id"         varchar(40) NOT NULL,
    "star_id"         varchar(30) NOT NULL,
    "user_id"         int8 NOT NULL,
    "name"            varchar(50) NOT NULL,
    "bio"             text,
    "avatar_url"      varchar(500),
    "status"          varchar(20) NOT NULL DEFAULT 'active',
    "contact_policy"  jsonb NOT NULL DEFAULT '{}',
    "timezone"        varchar(50) DEFAULT 'Asia/Shanghai',
    "tags"            text[],
    "stats"           jsonb NOT NULL DEFAULT '{}',
    "created_time"    timestamptz(6) NOT NULL DEFAULT now(),
    "updated_time"    timestamptz(6)
);

COMMENT ON TABLE "public"."hasn_humans" IS 'HASN 人类用户身份表';
COMMENT ON COLUMN "public"."hasn_humans"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_humans"."hasn_id" IS 'HASN 唯一标识 (h_{uuid})';
COMMENT ON COLUMN "public"."hasn_humans"."star_id" IS '唤星号 (数字号或自定义号)';
COMMENT ON COLUMN "public"."hasn_humans"."user_id" IS '关联唤星平台用户 ID';
COMMENT ON COLUMN "public"."hasn_humans"."name" IS '显示名称';
COMMENT ON COLUMN "public"."hasn_humans"."bio" IS '个人简介';
COMMENT ON COLUMN "public"."hasn_humans"."avatar_url" IS '头像 URL';
COMMENT ON COLUMN "public"."hasn_humans"."status" IS '状态 (active:正常:green/suspended:已暂停:orange/deleted:已注销:red)';
COMMENT ON COLUMN "public"."hasn_humans"."contact_policy" IS '联系人策略 (JSON: human_direct/via_agent/stranger_policy 等)';
COMMENT ON COLUMN "public"."hasn_humans"."timezone" IS '时区';
COMMENT ON COLUMN "public"."hasn_humans"."tags" IS '个人标签';
COMMENT ON COLUMN "public"."hasn_humans"."stats" IS '统计信息 (JSON: contacts_count/agents_count)';

CREATE UNIQUE INDEX "idx_hasn_humans_hasn_id" ON "public"."hasn_humans" ("hasn_id");
CREATE UNIQUE INDEX "idx_hasn_humans_star_id" ON "public"."hasn_humans" ("star_id");
CREATE UNIQUE INDEX "idx_hasn_humans_user_id" ON "public"."hasn_humans" ("user_id");
CREATE INDEX "idx_hasn_humans_status" ON "public"."hasn_humans" ("status");
