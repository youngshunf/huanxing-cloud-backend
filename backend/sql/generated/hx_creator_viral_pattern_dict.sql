-- =====================================================
-- 爆款模式库表 字典数据初始化 SQL
-- 自动生成于: 2026-03-05 19:20:11.661021
-- =====================================================

-- 分类：hook/structure/title/cta/visual/rhythm 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('分类：hook/structure/title/cta/visual/rhythm', 'creator_category', '爆款模式库表模块-分类：hook/structure/title/cta/visual/rhythm', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 分类：hook/structure/title/cta/visual/rhythm 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'creator_category' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_category' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('creator_category', '选项1', '1', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'creator_category' AND value = '2') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('creator_category', '选项2', '2', 'green', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================