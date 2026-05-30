-- 社区黑名单表（doc-13 §2.3.2）：一对多，UNIQUE(blocker, blocked)
CREATE TABLE IF NOT EXISTS "public"."hasn_community_blocks" (
  "id"               bigserial PRIMARY KEY,
  "blocker_hasn_id"  varchar(40) NOT NULL,
  "blocked_hasn_id"  varchar(40) NOT NULL,
  "blocked_type"     varchar(10) NOT NULL DEFAULT 'human',
  "reason"           varchar(200),
  "created_time"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_time"     timestamptz(6),
  UNIQUE("blocker_hasn_id", "blocked_hasn_id")
);

CREATE INDEX IF NOT EXISTS "idx_community_blocks_blocker"
  ON "public"."hasn_community_blocks" ("blocker_hasn_id");

COMMENT ON TABLE "public"."hasn_community_blocks" IS '社区黑名单表';
COMMENT ON COLUMN "public"."hasn_community_blocks"."blocker_hasn_id" IS '拉黑发起者 hasn_id';
COMMENT ON COLUMN "public"."hasn_community_blocks"."blocked_hasn_id" IS '被拉黑对象 hasn_id';
COMMENT ON COLUMN "public"."hasn_community_blocks"."blocked_type" IS '被拉黑对象类型 (human:用户:blue/agent:智能体:purple)';
COMMENT ON COLUMN "public"."hasn_community_blocks"."reason" IS '拉黑原因（可选）';
COMMENT ON COLUMN "public"."hasn_community_blocks"."created_time" IS '创建时间';
