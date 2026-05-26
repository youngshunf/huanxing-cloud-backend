-- 技能市场下载历史表
CREATE TABLE IF NOT EXISTS "public"."marketplace_download_history" (
  "id" bigserial PRIMARY KEY,
  "skill_id" varchar(100) NOT NULL,
  "version" varchar(50) NOT NULL,
  "user_id" int8,
  "ip_address" varchar(50),
  "user_agent" text,
  "downloaded_at" timestamptz(6) DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_download_skill ON marketplace_download_history(skill_id, downloaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_download_user ON marketplace_download_history(user_id, downloaded_at DESC);

-- 字段注释
COMMENT ON TABLE "public"."marketplace_download_history" IS '技能市场下载历史表';
COMMENT ON COLUMN "public"."marketplace_download_history"."id" IS '主键ID';
COMMENT ON COLUMN "public"."marketplace_download_history"."skill_id" IS '技能ID';
COMMENT ON COLUMN "public"."marketplace_download_history"."version" IS '版本号';
COMMENT ON COLUMN "public"."marketplace_download_history"."user_id" IS '用户ID';
COMMENT ON COLUMN "public"."marketplace_download_history"."ip_address" IS 'IP地址';
COMMENT ON COLUMN "public"."marketplace_download_history"."user_agent" IS '用户代理';
COMMENT ON COLUMN "public"."marketplace_download_history"."downloaded_at" IS '下载时间';
