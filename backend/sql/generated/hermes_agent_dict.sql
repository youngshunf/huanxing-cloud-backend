-- =====================================================
-- Hermes Agent 表 字典数据初始化 SQL
-- 自动生成于: 2026-04-29 18:20:38.414760
-- =====================================================

-- Agent状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Agent状态', 'hermes_status', 'Hermes Agent 表模块-Agent状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Agent状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'creating') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '创建中', 'creating', 'orange', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'created') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '已创建', 'created', 'blue', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'ready') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '就绪', 'ready', 'cyan', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'running') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '运行中', 'running', 'green', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'stopped') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '已停止', 'stopped', 'gray', 5, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'error') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '异常', 'error', 'red', 6, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'deleting') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '删除中', 'deleting', 'orange', 7, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_status' AND value = 'deleted') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_status', '已删除', 'deleted', 'gray', 8, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- Gateway状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Gateway状态', 'hermes_gateway_status', 'Hermes Agent 表模块-Gateway状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Gateway状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_gateway_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'stopped') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '已停止', 'stopped', 'gray', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'starting') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '启动中', 'starting', 'orange', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'running') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '运行中', 'running', 'green', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'restarting') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '重启中', 'restarting', 'orange', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'stopping') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '停止中', 'stopping', 'orange', 5, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'unhealthy') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '不健康', 'unhealthy', 'red', 6, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_gateway_status' AND value = 'error') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_gateway_status', '异常', 'error', 'red', 7, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- Workspace状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Workspace状态', 'hermes_workspace_status', 'Hermes Agent 表模块-Workspace状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Workspace状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_workspace_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_workspace_status' AND value = 'unknown') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_workspace_status', '未知', 'unknown', 'gray', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_workspace_status' AND value = 'ready') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_workspace_status', '就绪', 'ready', 'green', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_workspace_status' AND value = 'active') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_workspace_status', '运行中', 'active', 'blue', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_workspace_status' AND value = 'error') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_workspace_status', '异常', 'error', 'red', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- Sandbox状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Sandbox状态', 'hermes_sandbox_status', 'Hermes Agent 表模块-Sandbox状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Sandbox状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hermes_sandbox_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_sandbox_status' AND value = 'unknown') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_sandbox_status', '未知', 'unknown', 'gray', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_sandbox_status' AND value = 'ready') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_sandbox_status', '就绪', 'ready', 'green', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_sandbox_status' AND value = 'unprotected') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_sandbox_status', '未保护', 'unprotected', 'orange', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hermes_sandbox_status' AND value = 'error') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('hermes_sandbox_status', '异常', 'error', 'red', 4, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================