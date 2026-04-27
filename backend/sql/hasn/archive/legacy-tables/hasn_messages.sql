CREATE TABLE "public"."hasn_messages" (
    "id"                 bigserial PRIMARY KEY,
    "conversation_id"    uuid NOT NULL,
    "from_id"            varchar(40) NOT NULL,
    "from_type"          smallint NOT NULL DEFAULT 1,
    "to_id"              varchar(40) NOT NULL,
    "to_type"            smallint NOT NULL DEFAULT 1,
    "content_type"       smallint NOT NULL DEFAULT 1,
    "content"            jsonb NOT NULL,
    "msg_type"           varchar(30) NOT NULL DEFAULT 'message',
    "status"             smallint NOT NULL DEFAULT 1,
    "priority"           varchar(10) NOT NULL DEFAULT 'normal',
    "reply_to_id"        int8,
    "local_id"           uuid,
    "context"            jsonb,
    "recalled_at"        timestamptz(6),
    "recalled_by"        varchar(40),
    "edited_at"          timestamptz(6),
    "edit_version"       smallint NOT NULL DEFAULT 1,
    "server_received_at" timestamptz(6) NOT NULL DEFAULT now(),
    "created_time"       timestamptz(6) NOT NULL DEFAULT now(),
    "updated_time"       timestamptz(6)
);

COMMENT ON TABLE "public"."hasn_messages" IS 'HASN 消息表';
COMMENT ON COLUMN "public"."hasn_messages"."id" IS '消息 ID (BIGINT 自增，时间有序)';
COMMENT ON COLUMN "public"."hasn_messages"."conversation_id" IS '所属会话 ID';
COMMENT ON COLUMN "public"."hasn_messages"."from_id" IS '发送方 hasn_id';
COMMENT ON COLUMN "public"."hasn_messages"."from_type" IS '发送方类型 (1:人类/2:代理/3:系统)';
COMMENT ON COLUMN "public"."hasn_messages"."to_id" IS '接收方 hasn_id';
COMMENT ON COLUMN "public"."hasn_messages"."to_type" IS '接收方类型 (1:人类/2:代理/3:系统)';
COMMENT ON COLUMN "public"."hasn_messages"."content_type" IS '内容类型 (1:文本/2:图片/3:文件/4:语音/5:卡片/6:能力请求/7:能力响应)';
COMMENT ON COLUMN "public"."hasn_messages"."content" IS '消息内容 (JSON: {text/url/filename/...})';
COMMENT ON COLUMN "public"."hasn_messages"."msg_type" IS '消息类型 (message:普通消息/contact_request:好友请求/contact_accept:接受好友/contact_reject:拒绝好友/notification:通知/system:系统消息)';
COMMENT ON COLUMN "public"."hasn_messages"."status" IS '消息状态 (1:已发送:blue/2:已送达:cyan/3:已读:green/4:已撤回:red)';
COMMENT ON COLUMN "public"."hasn_messages"."priority" IS '优先级 (critical:紧急:red/high:高:orange/normal:普通:blue/low:低:gray)';
COMMENT ON COLUMN "public"."hasn_messages"."reply_to_id" IS '回复的消息 ID';
COMMENT ON COLUMN "public"."hasn_messages"."local_id" IS '客户端本地 ID (UUID, 用于去重)';
COMMENT ON COLUMN "public"."hasn_messages"."context" IS '消息上下文 (JSON: relation_type/scope/trade_session_id/thread_id 等)';
COMMENT ON COLUMN "public"."hasn_messages"."recalled_at" IS '撤回时间';
COMMENT ON COLUMN "public"."hasn_messages"."recalled_by" IS '撤回者 hasn_id';
COMMENT ON COLUMN "public"."hasn_messages"."edited_at" IS '最后编辑时间';
COMMENT ON COLUMN "public"."hasn_messages"."edit_version" IS '编辑版本号';
COMMENT ON COLUMN "public"."hasn_messages"."server_received_at" IS '服务端接收时间';

CREATE INDEX "idx_hasn_msg_conv_time" ON "public"."hasn_messages" ("conversation_id", "id" DESC);
CREATE INDEX "idx_hasn_msg_from" ON "public"."hasn_messages" ("from_id", "created_time" DESC);
CREATE INDEX "idx_hasn_msg_to" ON "public"."hasn_messages" ("to_id", "created_time" DESC);
CREATE INDEX "idx_hasn_msg_status" ON "public"."hasn_messages" ("conversation_id", "status");
CREATE UNIQUE INDEX "idx_hasn_msg_local_id" ON "public"."hasn_messages" ("local_id") WHERE "local_id" IS NOT NULL;
