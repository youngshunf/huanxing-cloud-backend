-- =====================================================
-- 唤星用户表 字典数据初始化 SQL
-- 自动生成于: 2026-02-27 11:22:24.178439
-- =====================================================

-- Agent状态：1-启用 0-禁用 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('Agent状态：1-启用 0-禁用', 'huanxing_agent_status', '唤星用户表模块-Agent状态：1-启用 0-禁用', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- Agent状态：1-启用 0-禁用 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'huanxing_agent_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_agent_status' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_agent_status', '启用', '1', 'green', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_agent_status' AND value = '0') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_agent_status', '禁用', '0', 'red', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- 注册渠道：feishu/qq/wechat 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('注册渠道：feishu/qq/wechat', 'huanxing_channel_type', '唤星用户表模块-注册渠道：feishu/qq/wechat', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 注册渠道：feishu/qq/wechat 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'huanxing_channel_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_channel_type' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_channel_type', '类型1', '1', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'huanxing_channel_type' AND value = '2') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('huanxing_channel_type', '类型2', '2', 'orange', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================