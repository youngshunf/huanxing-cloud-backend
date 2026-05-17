-- =====================================================
-- 用户身份映射管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-05-16 12:44:22.946303
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /bridge)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/bridge' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Bridge', 'Bridge', '/bridge', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'bridge模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /bridge/user_identity_mappings)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/bridge/user_identity_mappings' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('用户身份映射管理', 'UserIdentityMappings', '/bridge/user_identity_mappings', 1, 'lucide:list', 1, '/bridge/user_identity_mappings/index', NULL, 1, 1, 1, '', '用户身份映射表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = '用户身份映射管理',
            name = 'UserIdentityMappings',
            component = '/bridge/user_identity_mappings/index',
            remark = '用户身份映射表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'user:identity:mappings:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddUserIdentityMappings', NULL, 1, NULL, 2, NULL, 'user:identity:mappings:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'user:identity:mappings:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditUserIdentityMappings', NULL, 2, NULL, 2, NULL, 'user:identity:mappings:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'user:identity:mappings:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteUserIdentityMappings', NULL, 3, NULL, 2, NULL, 'user:identity:mappings:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'user:identity:mappings:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewUserIdentityMappings', NULL, 4, NULL, 2, NULL, 'user:identity:mappings:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
