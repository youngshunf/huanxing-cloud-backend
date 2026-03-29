-- =====================================================
-- Token 额度管理 菜单初始化 SQL (PostgreSQL)
-- 幂等：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找父级目录菜单 (path = /user_tier)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/user_tier' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('订阅管理', 'UserTier', '/user_tier', 3, 'carbon:currency', 0, 'BasicLayout', NULL, 1, 1, 1, '', '订阅与积分管理模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /user_tier/newapi_quota)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/user_tier/newapi_quota' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Token 额度管理', 'NewApiQuota', '/user_tier/newapi_quota', 2, 'carbon:meter-alt', 1, '/user_tier/newapi_quota/index', NULL, 1, 1, 1, '', '管理用户 API Token、额度和用量', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = 'Token 额度管理',
            name = 'NewApiQuota',
            component = '/user_tier/newapi_quota/index',
            remark = '管理用户 API Token、额度和用量',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 编辑额度按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'user:newapi:quota:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑额度', 'EditNewApiQuota', NULL, 1, NULL, 2, NULL, 'user:newapi:quota:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'user:newapi:quota:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewNewApiQuota', NULL, 2, NULL, 2, NULL, 'user:newapi:quota:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
