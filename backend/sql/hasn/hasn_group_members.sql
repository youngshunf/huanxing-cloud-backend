-- =====================================================
-- HASN 群成员表
-- 关联 hasn_conversations (type='group')
-- =====================================================
CREATE TABLE "public"."hasn_group_members" (
  "id"              bigserial PRIMARY KEY,
  "conversation_id" uuid NOT NULL,
  "member_id"       varchar(40) NOT NULL,
  "member_type"     varchar(10) NOT NULL,
  "member_star_id"  varchar(40) NOT NULL,
  "member_name"     varchar(100) NOT NULL,
  "role"            varchar(20) NOT NULL DEFAULT 'member',
  "muted"           boolean NOT NULL DEFAULT false,
  "joined_at"       timestamptz(6),
  "invited_by"      varchar(40),
  "created_time"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"    timestamptz(6),
  CONSTRAINT "uq_hasn_group_member" UNIQUE ("conversation_id", "member_id"),
  CONSTRAINT "fk_group_member_conv"
    FOREIGN KEY ("conversation_id") REFERENCES "public"."hasn_conversations"("id")
    ON DELETE CASCADE
);

CREATE INDEX "idx_group_member_conv" ON "public"."hasn_group_members" ("conversation_id");
CREATE INDEX "idx_group_member_user" ON "public"."hasn_group_members" ("member_id");

COMMENT ON TABLE "public"."hasn_group_members" IS 'HASN 群成员表';
COMMENT ON COLUMN "public"."hasn_group_members"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_group_members"."conversation_id" IS '群会话 ID（关联 hasn_conversations）';
COMMENT ON COLUMN "public"."hasn_group_members"."member_id" IS '成员 hasn_id';
COMMENT ON COLUMN "public"."hasn_group_members"."member_type" IS '成员类型 (human:人类:blue/agent:代理:green)';
COMMENT ON COLUMN "public"."hasn_group_members"."member_star_id" IS '成员唤星号';
COMMENT ON COLUMN "public"."hasn_group_members"."member_name" IS '成员名称';
COMMENT ON COLUMN "public"."hasn_group_members"."role" IS '角色 (owner:群主:red/admin:管理员:orange/member:成员:blue)';
COMMENT ON COLUMN "public"."hasn_group_members"."muted" IS '是否免打扰';
COMMENT ON COLUMN "public"."hasn_group_members"."joined_at" IS '加入时间';
COMMENT ON COLUMN "public"."hasn_group_members"."invited_by" IS '邀请者 hasn_id';
COMMENT ON COLUMN "public"."hasn_group_members"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_group_members"."updated_time" IS '更新时间';
