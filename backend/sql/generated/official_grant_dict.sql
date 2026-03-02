-- =============================================
-- 官方赠送(official_grant) 字典数据
-- 涉及: 积分类型、来源类型、交易类型
-- =============================================

-- 1. 积分类型 (user_tier_credit_type) 新增: 官方赠送
DO $$
DECLARE
    v_dict_type_id BIGINT;
BEGIN
    SELECT id INTO v_dict_type_id
    FROM sys_dict_type WHERE code = 'user_tier_credit_type'
    ORDER BY id DESC LIMIT 1;

    IF v_dict_type_id IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'user_tier_credit_type' AND value = 'official_grant')
    THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('user_tier_credit_type', '官方赠送', 'official_grant', 'purple', 4, 1, v_dict_type_id, '管理员手动赠送的积分', NOW());
    END IF;
END$$;

-- 2. 来源类型 (user_tier_source_type) 新增: 官方赠送
DO $$
DECLARE
    v_dict_type_id BIGINT;
BEGIN
    SELECT id INTO v_dict_type_id
    FROM sys_dict_type WHERE code = 'user_tier_source_type'
    ORDER BY id DESC LIMIT 1;

    IF v_dict_type_id IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'user_tier_source_type' AND value = 'official_grant')
    THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('user_tier_source_type', '官方赠送', 'official_grant', 'purple', 6, 1, v_dict_type_id, '管理员手动赠送', NOW());
    END IF;
END$$;

-- 3. 交易类型 (user_tier_transaction_type) 新增: 官方赠送
DO $$
DECLARE
    v_dict_type_id BIGINT;
BEGIN
    SELECT id INTO v_dict_type_id
    FROM sys_dict_type WHERE code = 'user_tier_transaction_type'
    ORDER BY id DESC LIMIT 1;

    IF v_dict_type_id IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM sys_dict_data WHERE type_code = 'user_tier_transaction_type' AND value = 'official_grant')
    THEN
        INSERT INTO sys_dict_data (type_code, label, value, color, sort, status, type_id, remark, created_time)
        VALUES ('user_tier_transaction_type', '官方赠送', 'official_grant', 'purple', 6, 1, v_dict_type_id, '管理员手动赠送积分', NOW());
    END IF;
END$$;
