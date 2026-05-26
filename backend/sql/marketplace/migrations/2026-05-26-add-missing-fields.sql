-- ============================================
-- 为现有表添加缺失字段
-- 日期：2026-05-26
-- ============================================

-- 为 marketplace_skill 添加缺失字段
ALTER TABLE marketplace_skill
ADD COLUMN IF NOT EXISTS namespace varchar(50),
ADD COLUMN IF NOT EXISTS slug varchar(100),
ADD COLUMN IF NOT EXISTS name_en varchar(200),
ADD COLUMN IF NOT EXISTS name_zh varchar(200),
ADD COLUMN IF NOT EXISTS description_en text,
ADD COLUMN IF NOT EXISTS description_zh text,
ADD COLUMN IF NOT EXISTS source_language varchar(10),
ADD COLUMN IF NOT EXISTS source_type varchar(20) DEFAULT 'github',
ADD COLUMN IF NOT EXISTS source_repo_url varchar(500),
ADD COLUMN IF NOT EXISTS source_repo_path varchar(500);

-- 创建索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_marketplace_skill_namespace_slug
ON marketplace_skill (namespace, slug);

CREATE INDEX IF NOT EXISTS idx_marketplace_skill_source_type
ON marketplace_skill (source_type);

-- 添加注释
COMMENT ON COLUMN marketplace_skill.namespace IS '命名空间（如 huanxing/clawhub）';
COMMENT ON COLUMN marketplace_skill.slug IS '技能标识符（如 translator-pro）';
COMMENT ON COLUMN marketplace_skill.name_en IS '英文名称';
COMMENT ON COLUMN marketplace_skill.name_zh IS '中文名称';
COMMENT ON COLUMN marketplace_skill.description_en IS '英文描述';
COMMENT ON COLUMN marketplace_skill.description_zh IS '中文描述';
COMMENT ON COLUMN marketplace_skill.source_language IS '源语言（en/zh）';
COMMENT ON COLUMN marketplace_skill.source_type IS '来源类型 (github/clawhub/local)';
COMMENT ON COLUMN marketplace_skill.source_repo_url IS '源仓库 URL';
COMMENT ON COLUMN marketplace_skill.source_repo_path IS '仓库内路径';
