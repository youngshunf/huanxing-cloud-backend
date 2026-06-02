-- =====================================================
-- 统一通知服务 P1：主人通知偏好表
-- 设计事实源：docs/hasn-node设计文档/通知系统统一设计/00-统一通知服务设计.md §4.4
-- 最终投递策略 = category 默认 ⊕ 主人偏好覆盖 ⊕ 来源 delivery_hint
-- =====================================================
CREATE TABLE IF NOT EXISTS "public"."hasn_notification_preferences" (
  "id"           bigserial PRIMARY KEY,
  "owner_id"     varchar(40) NOT NULL,
  "category"     varchar(20) NOT NULL,
  "channels"     jsonb NOT NULL DEFAULT '{}',
  "dnd"          jsonb NOT NULL DEFAULT '{}',
  "created_time" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time" timestamptz(6)
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_notif_pref_owner_category"
  ON "public"."hasn_notification_preferences" ("owner_id","category");

COMMENT ON TABLE "public"."hasn_notification_preferences" IS 'HASN 主人通知偏好表';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."owner_id" IS '主人 hasn_id';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."category" IS '通知粗类，或 * 表全局默认';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."channels" IS '渠道开关 {center,card_message,toast,push}';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."dnd" IS '免打扰 {enabled,start,end,tz,allow_critical}';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."created_time" IS '创建时间';
COMMENT ON COLUMN "public"."hasn_notification_preferences"."updated_time" IS '更新时间';
