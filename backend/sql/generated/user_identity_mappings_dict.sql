-- =====================================================
-- 用户身份映射表 字典数据初始化 SQL
-- 自动生成于: 2026-05-16 12:44:23.512219
-- =====================================================

-- 映射类型 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('映射类型', 'bridge_mapping_type', '用户身份映射表模块-映射类型', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 映射类型 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'bridge_mapping_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_mapping_type' AND value = 'oauth_linked') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_mapping_type', 'OAuth授权', 'oauth_linked', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_mapping_type' AND value = 'manual_linked') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_mapping_type', '手动关联', 'manual_linked', 'gray', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_mapping_type' AND value = 'auto_provisioned') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_mapping_type', '自动创建', 'auto_provisioned', 'green', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- oauth_token_type 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('oauth_token_type', 'bridge_oauth_token_type', '用户身份映射表模块-oauth_token_type', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- oauth_token_type 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'bridge_oauth_token_type' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_oauth_token_type' AND value = '1') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_oauth_token_type', '类型1', '1', 'blue', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_oauth_token_type' AND value = '2') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_oauth_token_type', '类型2', '2', 'orange', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- 状态 字典类型
INSERT INTO sys_dict_type (name, code, remark, created_time, updated_time)
VALUES
('状态', 'bridge_status', '用户身份映射表模块-状态', NOW(), NULL)
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, remark = EXCLUDED.remark, updated_time = NOW();

-- 状态 字典数据
DO $$
DECLARE
    v_dict_type_id INTEGER;
BEGIN
    SELECT id INTO v_dict_type_id FROM sys_dict_type
    WHERE code = 'bridge_status' ORDER BY id DESC LIMIT 1;

    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_status' AND value = 'active') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_status', '活跃', 'active', 'green', 1, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_status' AND value = 'expired') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_status', '已过期', 'expired', 'orange', 2, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'bridge_status' AND value = 'revoked') THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time, updated_time)
        VALUES ('bridge_status', '已撤销', 'revoked', 'red', 3, 1, v_dict_type_id, '', NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 字典数据生成完成
-- =====================================================