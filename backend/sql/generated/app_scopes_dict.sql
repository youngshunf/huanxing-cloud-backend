-- =====================================================
-- 应用权限定义表（{domain}.* namespace） 字典数据初始化 SQL
-- 自动生成于: 2026-05-14 13:08:14.559093
-- =====================================================

-- 风险等级 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('风险等级', 'app_platform_risk_level', '应用权限定义表（{domain}.* namespace）模块-风险等级', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 风险等级 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'app_platform_risk_level' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'app_platform_risk_level' AND value = 'low') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('app_platform_risk_level', '低风险', 'low', 'green', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'app_platform_risk_level' AND value = 'medium') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('app_platform_risk_level', '中风险', 'medium', 'orange', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'app_platform_risk_level' AND value = 'high') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('app_platform_risk_level', '高风险', 'high', 'red', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================