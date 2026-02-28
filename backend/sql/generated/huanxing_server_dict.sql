-- =====================================================
-- 唤星服务器表 字典数据初始化 SQL
-- 自动生成于: 2026-02-27 11:22:23.966314
-- =====================================================

-- 状态：1-启用 0-禁用 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('状态：1-启用 0-禁用', 'huanxing_status', '唤星服务器表模块-状态：1-启用 0-禁用', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 状态：1-启用 0-禁用 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'huanxing_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_status' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_status', '启用', '1', 'green', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_status' AND value = '0') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_status', '禁用', '0', 'red', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- Gateway状态: running/stopped/unknown 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Gateway状态: running/stopped/unknown', 'huanxing_gateway_status', '唤星服务器表模块-Gateway状态: running/stopped/unknown', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Gateway状态: running/stopped/unknown 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'huanxing_gateway_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_gateway_status' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_gateway_status', '启用', '1', 'green', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_gateway_status' AND value = '0') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_gateway_status', '禁用', '0', 'red', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================