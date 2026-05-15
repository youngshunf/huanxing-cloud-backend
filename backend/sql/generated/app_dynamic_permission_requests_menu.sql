-- =====================================================
-- 动态权限请求管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-05-14 13:08:27.800023
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

    -- 查找或创建主菜单 (path = /app_platform/app_dynamic_permission_requests)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/app_platform/app_dynamic_permission_requests' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('动态权限请求管理', 'AppDynamicPermissionRequests', '/app_platform/app_dynamic_permission_requests', 1, 'lucide:list', 1, '/app_platform/app_dynamic_permission_requests/index', NULL, 1, 1, 1, '', '动态权限请求表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = '动态权限请求管理',
            name = 'AppDynamicPermissionRequests',
            component = '/app_platform/app_dynamic_permission_requests/index',
            remark = '动态权限请求表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:dynamic:permission:requests:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddAppDynamicPermissionRequests', NULL, 1, NULL, 2, NULL, 'app:dynamic:permission:requests:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:dynamic:permission:requests:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditAppDynamicPermissionRequests', NULL, 2, NULL, 2, NULL, 'app:dynamic:permission:requests:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:dynamic:permission:requests:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteAppDynamicPermissionRequests', NULL, 3, NULL, 2, NULL, 'app:dynamic:permission:requests:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'app:dynamic:permission:requests:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewAppDynamicPermissionRequests', NULL, 4, NULL, 2, NULL, 'app:dynamic:permission:requests:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
