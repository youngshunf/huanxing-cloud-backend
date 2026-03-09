-- =====================================================
-- HASN 审计日志表 字典数据初始化 SQL
-- 修复: hasn_target_type 补充完整选项
-- =====================================================

-- 操作者类型: human/agent/system 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('操作者类型', 'hasn_actor_type', 'HASN审计日志-操作者类型: human/agent/system', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 操作者类型 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hasn_actor_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_actor_type' AND value = 'human') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_actor_type', '用户', 'human', 'blue', 1, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_actor_type' AND value = 'agent') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_actor_type', 'Agent', 'agent', 'purple', 2, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_actor_type' AND value = 'system') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_actor_type', '系统', 'system', 'default', 3, 1, v_dict_type_id, '', NOW());
    END IF;
END $$;

-- 目标类型 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('目标类型', 'hasn_target_type', 'HASN审计日志-目标类型: human/agent/conversation/message/contact/system', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 目标类型 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'hasn_target_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_target_type' AND value = 'human') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_target_type', '用户', 'human', 'blue', 1, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_target_type' AND value = 'agent') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_target_type', 'Agent', 'agent', 'purple', 2, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_target_type' AND value = 'conversation') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_target_type', '会话', 'conversation', 'cyan', 3, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_target_type' AND value = 'message') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_target_type', '消息', 'message', 'green', 4, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_target_type' AND value = 'contact') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_target_type', '联系人', 'contact', 'orange', 5, 1, v_dict_type_id, '', NOW());
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'hasn_target_type' AND value = 'system') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('hasn_target_type', '系统', 'system', 'default', 6, 1, v_dict_type_id, '', NOW());
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================
