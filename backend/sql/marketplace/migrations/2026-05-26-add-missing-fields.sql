-- ============================================
-- 为现有表添加缺失字段
-- 日期：2026-05-26
-- ============================================

-- 为 marketplace_skill 添加缺失字段
ALTER TABLE marketplace_skill
ADD COLUMN IF NOT EXISTS namespace varchar(160),
ADD COLUMN IF NOT EXISTS slug varchar(100),
ADD COLUMN IF NOT EXISTS user_id int8,
ADD COLUMN IF NOT EXISTS hasn_id varchar(40),
ADD COLUMN IF NOT EXISTS status varchar(20) NOT NULL DEFAULT 'published',
ADD COLUMN IF NOT EXISTS visibility varchar(20) NOT NULL DEFAULT 'public',
ADD COLUMN IF NOT EXISTS reviewed_by int8,
ADD COLUMN IF NOT EXISTS reviewed_at timestamptz(6),
ADD COLUMN IF NOT EXISTS review_note text,
ADD COLUMN IF NOT EXISTS published_at timestamptz(6),
ADD COLUMN IF NOT EXISTS suspended_at timestamptz(6),
ADD COLUMN IF NOT EXISTS suspend_reason text,
ADD COLUMN IF NOT EXISTS name varchar(200) NOT NULL DEFAULT '',
ADD COLUMN IF NOT EXISTS name_en varchar(200),
ADD COLUMN IF NOT EXISTS name_zh varchar(200),
ADD COLUMN IF NOT EXISTS description_en text,
ADD COLUMN IF NOT EXISTS description_zh text,
ADD COLUMN IF NOT EXISTS source_language varchar(10),
ADD COLUMN IF NOT EXISTS tags_en text,
ADD COLUMN IF NOT EXISTS tags_zh text,
ADD COLUMN IF NOT EXISTS source_type varchar(20) DEFAULT 'github',
ADD COLUMN IF NOT EXISTS source_repo_url varchar(500),
ADD COLUMN IF NOT EXISTS source_repo_path varchar(500);

ALTER TABLE marketplace_skill
ALTER COLUMN reviewed_at TYPE timestamptz(6) USING reviewed_at AT TIME ZONE 'Asia/Shanghai',
ALTER COLUMN published_at TYPE timestamptz(6) USING published_at AT TIME ZONE 'Asia/Shanghai',
ALTER COLUMN suspended_at TYPE timestamptz(6) USING suspended_at AT TIME ZONE 'Asia/Shanghai',
ALTER COLUMN synced_at TYPE timestamptz(6) USING synced_at AT TIME ZONE 'Asia/Shanghai',
ALTER COLUMN translated_at TYPE timestamptz(6) USING translated_at AT TIME ZONE 'Asia/Shanghai';

-- 创建索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_marketplace_skill_namespace_slug
ON marketplace_skill (namespace, slug);

CREATE INDEX IF NOT EXISTS idx_marketplace_skill_source_type
ON marketplace_skill (source_type);

CREATE INDEX IF NOT EXISTS idx_marketplace_skill_user_id
ON marketplace_skill (user_id);

CREATE INDEX IF NOT EXISTS idx_marketplace_skill_hasn_id
ON marketplace_skill (hasn_id);

CREATE INDEX IF NOT EXISTS idx_marketplace_skill_status_visibility
ON marketplace_skill (status, visibility);

-- 添加注释
COMMENT ON COLUMN marketplace_skill.namespace IS '命名空间（如 huanxing/clawhub）';
COMMENT ON COLUMN marketplace_skill.slug IS '技能标识符（如 translator-pro）';
COMMENT ON COLUMN marketplace_skill.user_id IS '资源所有者用户ID';
COMMENT ON COLUMN marketplace_skill.hasn_id IS '资源所有者 HASN ID';
COMMENT ON COLUMN marketplace_skill.status IS '发布状态';
COMMENT ON COLUMN marketplace_skill.visibility IS '可见性';
COMMENT ON COLUMN marketplace_skill.reviewed_by IS '审核人用户ID';
COMMENT ON COLUMN marketplace_skill.reviewed_at IS '审核时间';
COMMENT ON COLUMN marketplace_skill.review_note IS '审核备注';
COMMENT ON COLUMN marketplace_skill.published_at IS '发布时间';
COMMENT ON COLUMN marketplace_skill.suspended_at IS '封禁时间';
COMMENT ON COLUMN marketplace_skill.suspend_reason IS '封禁原因';
COMMENT ON COLUMN marketplace_skill.name IS '技能名称';
COMMENT ON COLUMN marketplace_skill.name_en IS '英文名称';
COMMENT ON COLUMN marketplace_skill.name_zh IS '中文名称';
COMMENT ON COLUMN marketplace_skill.description_en IS '英文描述';
COMMENT ON COLUMN marketplace_skill.description_zh IS '中文描述';
COMMENT ON COLUMN marketplace_skill.source_language IS '源语言（en/zh）';
COMMENT ON COLUMN marketplace_skill.tags_en IS '英文标签，JSON数组字符串';
COMMENT ON COLUMN marketplace_skill.tags_zh IS '中文标签，JSON数组字符串';
COMMENT ON COLUMN marketplace_skill.source_type IS '来源类型 (huanxing/github/clawhub)';
COMMENT ON COLUMN marketplace_skill.source_repo_url IS '源仓库 URL';
COMMENT ON COLUMN marketplace_skill.source_repo_path IS '仓库内路径';
