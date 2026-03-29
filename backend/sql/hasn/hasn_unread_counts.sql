-- =====================================================
-- HASN 未读计数表
-- =====================================================
CREATE TABLE "public"."hasn_unread_counts" (
  "id"               bigserial PRIMARY KEY,
  "hasn_id"          varchar(40) NOT NULL,
  "conversation_id"  uuid NOT NULL,
  "unread_count"     int4 NOT NULL DEFAULT 0,
  "last_read_msg_id" int8 NOT NULL DEFAULT 0,
  "created_time"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"     timestamptz(6)
);

CREATE UNIQUE INDEX "idx_hasn_unread_user_conv" ON "public"."hasn_unread_counts" ("hasn_id", "conversation_id");
CREATE INDEX "idx_hasn_unread_hasn_id" ON "public"."hasn_unread_counts" ("hasn_id");

COMMENT ON TABLE "public"."hasn_unread_counts" IS 'HASN 未读计数表';
COMMENT ON COLUMN "public"."hasn_unread_counts"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_unread_counts"."hasn_id" IS '用户/Agent 的 hasn_id';
COMMENT ON COLUMN "public"."hasn_unread_counts"."conversation_id" IS '会话 ID';
COMMENT ON COLUMN "public"."hasn_unread_counts"."unread_count" IS '未读消息数';
COMMENT ON COLUMN "public"."hasn_unread_counts"."last_read_msg_id" IS '最后已读消息 ID';
COMMENT ON COLUMN "public"."hasn_unread_counts"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_unread_counts"."updated_time" IS '更新时间';
