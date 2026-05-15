-- =====================================================
-- 权限授予记录管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-05-14 13:08:24.760995
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /app_platform)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/app_platform' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('App Platform', 'App_platform', '/app_platform', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'app_platform模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /app_platform/app_permission_grants)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/app_platform/app_permission_grants' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('权限授予记录管理', 'AppPermissionGrants', '/app_platform/app_permission_grants', 1, 'lucide:list', 1, '/app_platform/app_permission_grants/index', NULL, 1, 1, 1, '', '权限授予记录表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = '权限授予记录管理',
            name = 'AppPermissionGrants',
            component = '/app_platform/app_permission_grants/index',
            remark = '权限授予记录表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:permission:grants:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddAppPermissionGrants', NULL, 1, NULL, 2, NULL, 'app:permission:grants:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:permission:grants:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditAppPermissionGrants', NULL, 2, NULL, 2, NULL, 'app:permission:grants:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:permission:grants:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteAppPermissionGrants', NULL, 3, NULL, 2, NULL, 'app:permission:grants:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:permission:grants:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewAppPermissionGrants', NULL, 4, NULL, 2, NULL, 'app:permission:grants:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
