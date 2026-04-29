-- =====================================================
--  菜单初始化 SQL (MySQL)
-- 自动生成于: 2026-04-29 18:20:35.939261+08:00
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

-- 查找父级目录菜单 (path = /hermes)
SET @parent_id = (SELECT id FROM sys_menu WHERE path = '/hermes' AND type = 0 ORDER BY id LIMIT 1);

-- 如果父级目录不存在，创建它
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '', 'Hermes', '/hermes', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'hermes模块', NULL, NOW(), NULL
FROM DUAL WHERE @parent_id IS NULL;

-- 重新获取父级目录 ID
SET @parent_id = COALESCE(@parent_id, LAST_INSERT_ID());

-- 查找主菜单 (path = /hermes/hermes_agent)
SET @menu_id = (SELECT id FROM sys_menu WHERE path = '/hermes/hermes_agent' AND type = 1 ORDER BY id LIMIT 1);

-- 如果主菜单不存在，创建它
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '', 'HermesAgent', '/hermes/hermes_agent', 1, 'lucide:list', 1, '/hermes/hermes_agent/index', NULL, 1, 1, 1, '', 'Hermes Agent ', @parent_id, NOW(), NULL
FROM DUAL WHERE @menu_id IS NULL;

-- 如果已存在，更新它
UPDATE sys_menu SET
    title = '',
    name = 'HermesAgent',
    component = '/hermes/hermes_agent/index',
    remark = 'Hermes Agent ',
    parent_id = @parent_id,
    updated_time = NOW()
WHERE id = @menu_id AND @menu_id IS NOT NULL;

-- 重新获取菜单 ID
SET @menu_id = COALESCE(@menu_id, LAST_INSERT_ID());

-- 新增按钮（不存在则插入）
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '新增', 'AddHermesAgent', NULL, 1, NULL, 2, NULL, 'hermes:agent:add', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:add' AND parent_id = @menu_id);

-- 编辑按钮
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '编辑', 'EditHermesAgent', NULL, 2, NULL, 2, NULL, 'hermes:agent:edit', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:edit' AND parent_id = @menu_id);

-- 删除按钮
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '删除', 'DeleteHermesAgent', NULL, 3, NULL, 2, NULL, 'hermes:agent:del', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:del' AND parent_id = @menu_id);

-- 查看按钮
INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
SELECT '查看', 'ViewHermesAgent', NULL, 4, NULL, 2, NULL, 'hermes:agent:get', 1, 0, 1, '', NULL, @menu_id, NOW(), NULL
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:get' AND parent_id = @menu_id);

-- =====================================================
-- 菜单生成完成
-- =====================================================
