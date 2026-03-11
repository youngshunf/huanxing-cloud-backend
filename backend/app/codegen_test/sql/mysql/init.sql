-- =====================================================
--  菜单初始化 SQL (MySQL)
-- 自动生成于: 2026-03-12 00:18:08.244309+08:00
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

-- 查找父级目录菜单 (path = /codegen_test)
SET @parent_id = (SELECT id FROM sys_menu WHERE path = '/codegen_test' AND type = 0 ORDER BY id LIMIT 1);

-- 如果父级目录不存在，创建它
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '', 'Codegen_test', '/codegen_test', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'codegen_test模块', NULL, NOW(), NULL
FROM DUAL WHERE @parent_id IS NULL;

-- 重新获取父级目录 ID
SET @parent_id = COALESCE(@parent_id, LAST_INSERT_ID());

-- 查找主菜单 (path = /codegen_test/codegen_test_task)
SET @menu_id = (SELECT id FROM sys_menu WHERE path = '/codegen_test/codegen_test_task' AND type = 1 ORDER BY id LIMIT 1);

-- 如果主菜单不存在，创建它
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '', 'CodegenTestTask', '/codegen_test/codegen_test_task', 1, 'lucide:list', 1, '/codegen_test/codegen_test_task/index', NULL, 1, 1, 1, '', '测试任务', @parent_id, NOW(), NULL
FROM DUAL WHERE @menu_id IS NULL;

-- 如果已存在，更新它
UPDATE sys_menu SET
    title = '',
    name = 'CodegenTestTask',
    component = '/codegen_test/codegen_test_task/index',
    remark = '测试任务',
    parent_id = @parent_id,
    updated_time = NOW()
WHERE id = @menu_id AND @menu_id IS NOT NULL;

-- 重新获取菜单 ID
SET @menu_id = COALESCE(@menu_id, LAST_INSERT_ID());

-- 新增按钮（不存在则插入）
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '新增', 'AddCodegenTestTask', NULL, 1, NULL, 2, NULL, 'codegen:test:task:add', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:add' AND parent_id = @menu_id);

-- 编辑按钮
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '编辑', 'EditCodegenTestTask', NULL, 2, NULL, 2, NULL, 'codegen:test:task:edit', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:edit' AND parent_id = @menu_id);

-- 删除按钮
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '删除', 'DeleteCodegenTestTask', NULL, 3, NULL, 2, NULL, 'codegen:test:task:del', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:del' AND parent_id = @menu_id);

-- 查看按钮
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '查看', 'ViewCodegenTestTask', NULL, 4, NULL, 2, NULL, 'codegen:test:task:get', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'codegen:test:task:get' AND parent_id = @menu_id);

-- =====================================================
-- 菜单生成完成
-- =====================================================
