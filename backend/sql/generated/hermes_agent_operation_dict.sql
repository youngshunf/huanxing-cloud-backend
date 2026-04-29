-- =====================================================
-- Hermes Agent 操作记录表 字典数据初始化 SQL
-- 自动生成于: 2026-04-29 18:20:54.225562
-- =====================================================

-- 操作类型 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('操作类型', 'hermes_operation_type', 'Hermes Agent 操作记录表模块-操作类型', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 操作类型 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_operation_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'create_agent') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '创建', 'create_agent', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'update_agent') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '更新', 'update_agent', 'blue', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'delete_agent') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '删除', 'delete_agent', 'red', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'start_gateway') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '启动', 'start_gateway', 'green', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'restart_gateway') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '重启', 'restart_gateway', 'orange', 5, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'stop_gateway') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '停止', 'stop_gateway', 'gray', 6, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'bind_channel') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '绑定', 'bind_channel', 'purple', 7, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'unbind_channel') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '解绑', 'unbind_channel', 'orange', 8, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'chat') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '对话', 'chat', 'green', 9, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'run') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '运行', 'run', 'cyan', 10, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_type' AND value = 'sync_runtime') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_type', '同步', 'sync_runtime', 'blue', 11, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- 操作状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('操作状态', 'hermes_operation_status', 'Hermes Agent 操作记录表模块-操作状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 操作状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_operation_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_status' AND value = 'started') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_status', '已开始', 'started', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_status' AND value = 'succeeded') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_status', '成功', 'succeeded', 'green', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_status' AND value = 'failed') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_status', '失败', 'failed', 'red', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_operation_status' AND value = 'cancelled') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_operation_status', '已取消', 'cancelled', 'gray', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================