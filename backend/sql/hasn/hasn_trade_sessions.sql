-- =====================================================
-- HASN 交易会话表
-- 对应协议: Layer 2 §4.3 Trade Session
-- Commerce 和 Service 类通信 MUST 关联到一个 Trade Session
-- =====================================================
CREATE TABLE "public"."hasn_trade_sessions" (
  "id"            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "buyer_id"      varchar(40) NOT NULL,
  "seller_id"     varchar(40) NOT NULL,
  "relation_type" varchar(20) NOT NULL,
  "scope"         varchar(30) NOT NULL DEFAULT 'pre_sale',
  "status"        varchar(20) NOT NULL DEFAULT 'active',
  "order_id"      varchar(100),
  "expires_at"    timestamptz(6),
  "metadata"      jsonb NOT NULL DEFAULT '{}',
  "created_time"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"  timestamptz(6)
);

CREATE INDEX "idx_trade_buyer" ON "public"."hasn_trade_sessions" ("buyer_id");
CREATE INDEX "idx_trade_seller" ON "public"."hasn_trade_sessions" ("seller_id");
CREATE INDEX "idx_trade_status" ON "public"."hasn_trade_sessions" ("status");
CREATE INDEX "idx_trade_expires" ON "public"."hasn_trade_sessions" ("expires_at") WHERE expires_at IS NOT NULL;

COMMENT ON TABLE "public"."hasn_trade_sessions" IS 'HASN 交易会话表';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."id" IS '交易会话 ID (UUID)';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."buyer_id" IS '买方 hasn_id';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."seller_id" IS '卖方 hasn_id';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."relation_type" IS '关系类型 (commerce:商业:orange/service:履约:green)';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."scope" IS '当前作用域 (commerce: pre_sale:售前:blue/negotiation:协商:cyan/in_order:订单中:orange/fulfilling:履约中:violet/after_sale:售后:green/subscription:订阅:purple | service: active_order:活跃订单:cyan | professional: consultation:咨询:blue/treatment:进行中:orange/follow_up:跟进:green | platform: app_installation:应用安装:gray/system_notice:系统通知:gray)';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."status" IS '状态 (active:进行中:green/completed:已完成:blue/archived:已归档:gray/cancelled:已取消:red)';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."order_id" IS '关联订单 ID';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."expires_at" IS '过期时间';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."metadata" IS '附加元数据 (JSONB)';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_trade_sessions"."updated_time" IS '更新时间';
