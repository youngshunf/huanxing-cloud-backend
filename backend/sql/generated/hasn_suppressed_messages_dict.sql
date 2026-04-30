-- =====================================================
-- HASN Runtime 抑制箱 / owner 可拉取消息表 字典数据初始化 SQL
-- 自动生成于: 2026-05-01 00:23:50.304203
-- =====================================================

-- Runtime 调度状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Runtime 调度状态', 'hasn_dispatch_status', 'HASN Runtime 抑制箱 / owner 可拉取消息表模块-Runtime 调度状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Runtime 调度状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hasn_dispatch_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_dispatch_status' AND value = 'runtime_unavailable') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hasn_dispatch_status', 'Runtime不可用', 'runtime_unavailable', 'orange', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_dispatch_status' AND value = 'dispatch_failed') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hasn_dispatch_status', '派发失败', 'dispatch_failed', 'red', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_dispatch_status' AND value = 'suppressed_by_policy') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hasn_dispatch_status', '策略抑制', 'suppressed_by_policy', 'purple', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_dispatch_status' AND value = 'pending_runtime') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hasn_dispatch_status', '等待Runtime', 'pending_runtime', 'blue', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================