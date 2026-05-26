-- 用户第三方应用凭证表
CREATE TABLE "public"."integration_credentials" (
  "id" bigserial PRIMARY KEY,
  "user_id" int8 NOT NULL,
  "app_id" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "credentials" jsonb NOT NULL,
  "is_active" bool NOT NULL DEFAULT true,
  "expires_at" timestamptz(6),
  "created_time" timestamptz(6) NOT NULL DEFAULT NOW(),
  "updated_time" timestamptz(6),
  UNIQUE("user_id", "app_id")
);

CREATE INDEX "idx_integration_credentials_user_id" ON "public"."integration_credentials" ("user_id");
CREATE INDEX "idx_integration_credentials_app_id" ON "public"."integration_credentials" ("app_id");
CREATE INDEX "idx_integration_credentials_is_active" ON "public"."integration_credentials" ("is_active");

COMMENT ON COLUMN "public"."integration_credentials"."id" IS '主键 ID';
COMMENT ON COLUMN "public"."integration_credentials"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."integration_credentials"."app_id" IS '应用唯一标识';
COMMENT ON COLUMN "public"."integration_credentials"."credentials" IS '凭证信息（JSON 格式，如 API Key、Access Token 等）';
COMMENT ON COLUMN "public"."integration_credentials"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."integration_credentials"."expires_at" IS '凭证过期时间';
COMMENT ON TABLE "public"."integration_credentials" IS '用户第三方应用凭证表';
