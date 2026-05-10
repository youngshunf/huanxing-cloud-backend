-- =====================================================
-- AI lead automation source configuration 字典数据初始化 SQL
-- 自动生成于: 2026-05-10 21:06:33.571093
-- =====================================================

-- source_type 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('source_type', 'lead_automation_source_type', 'AI lead automation source configuration模块-source_type', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- source_type 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'lead_automation_source_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'lead_automation_source_type' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('lead_automation_source_type', '类型1', '1', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'lead_automation_source_type' AND value = '2') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('lead_automation_source_type', '类型2', '2', 'orange', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================