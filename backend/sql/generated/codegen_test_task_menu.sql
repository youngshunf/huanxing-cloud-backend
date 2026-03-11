-- =====================================================
-- 测试任务管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-03-12 00:18:08.395378
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /codegen_test)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/codegen_test' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Codegen Test', 'Codegen_test', '/codegen_test', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'codegen_test模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /codegen_test/codegen_test_task)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/codegen_test/codegen_test_task' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('测试任务管理', 'CodegenTestTask', '/codegen_test/codegen_test_task', 1, 'lucide:list', 1, '/codegen_test/codegen_test_task/index', NULL, 1, 1, 1, '', '测试任务表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = '测试任务管理',
            name = 'CodegenTestTask',
            component = '/codegen_test/codegen_test_task/index',
            remark = '测试任务表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddCodegenTestTask', NULL, 1, NULL, 2, NULL, 'codegen:test:task:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditCodegenTestTask', NULL, 2, NULL, 2, NULL, 'codegen:test:task:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteCodegenTestTask', NULL, 3, NULL, 2, NULL, 'codegen:test:task:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewCodegenTestTask', NULL, 4, NULL, 2, NULL, 'codegen:test:task:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
