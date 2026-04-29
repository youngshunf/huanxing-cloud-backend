-- =====================================================
-- Hermes Agent 渠道绑定表 字典数据初始化 SQL
-- 自动生成于: 2026-04-29 18:20:48.211478
-- =====================================================

-- 状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('状态', 'hermes_status', 'Hermes Agent 渠道绑定表模块-状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'unbound') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '未绑', 'unbound', 'gray', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'created') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '创建', 'created', 'blue', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'qr_ready') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', 'QR', 'qr_ready', 'blue', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'waiting_scan') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '待扫', 'waiting_scan', 'orange', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'scanned') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '已扫', 'scanned', 'orange', 5, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'confirmed') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '确认', 'confirmed', 'blue', 6, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'writing_config') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '写', 'writing_config', 'orange', 7, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'restarting_gateway') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '重启', 'restarting_gateway', 'orange', 8, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'testing_connection') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '测试', 'testing_connection', 'blue', 9, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'bound') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '绑定', 'bound', 'green', 10, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'expired') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '过期', 'expired', 'gray', 11, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'failed') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '失败', 'failed', 'red', 12, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'cancelled') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '取消', 'cancelled', 'gray', 13, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================