-- 添加技能市场多语言字段
-- 2026-05-26

-- 添加多语言字段
ALTER TABLE marketplace_skill
ADD COLUMN IF NOT EXISTS name_en varchar(200),
ADD COLUMN IF NOT EXISTS name_zh varchar(200),
ADD COLUMN IF NOT EXISTS description_en text,
ADD COLUMN IF NOT EXISTS description_zh text,
ADD COLUMN IF NOT EXISTS source_language varchar(10),
ADD COLUMN IF NOT EXISTS tags_en text,
ADD COLUMN IF NOT EXISTS tags_zh text;

-- 如果存在旧的 name 和 description 字段，迁移数据
DO $$
BEGIN
    -- 检查是否存在 name 列
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'marketplace_skill' AND column_name = 'name'
    ) THEN
        -- 迁移 name 到 name_zh（假设原始数据是中文）
        UPDATE marketplace_skill
        SET name_zh = name, source_language = 'zh'
        WHERE name IS NOT NULL AND name_zh IS NULL;
    END IF;

    -- 检查是否存在 description 列
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'marketplace_skill' AND column_name = 'description'
    ) THEN
        -- 迁移 description 到 description_zh
        UPDATE marketplace_skill
        SET description_zh = description
        WHERE description IS NOT NULL AND description_zh IS NULL;
    END IF;
END $$;

-- 添加字段注释
COMMENT ON COLUMN marketplace_skill.name_en IS '英文名称';
COMMENT ON COLUMN marketplace_skill.name_zh IS '中文名称';
COMMENT ON COLUMN marketplace_skill.description_en IS '英文描述';
COMMENT ON COLUMN marketplace_skill.description_zh IS '中文描述';
COMMENT ON COLUMN marketplace_skill.source_language IS '原始语言 (en/zh)';
COMMENT ON COLUMN marketplace_skill.tags_en IS '英文标签，JSON数组字符串';
COMMENT ON COLUMN marketplace_skill.tags_zh IS '中文标签，JSON数组字符串';

-- 添加普通索引用于搜索（不使用全文搜索）
CREATE INDEX IF NOT EXISTS idx_marketplace_skill_name_zh ON marketplace_skill(name_zh);
CREATE INDEX IF NOT EXISTS idx_marketplace_skill_name_en ON marketplace_skill(name_en);
