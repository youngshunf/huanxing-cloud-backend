-- =====================================================
-- Hermes管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-04-29 18:20:37.198887
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /hermes)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/hermes' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Hermes', 'Hermes', '/hermes', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'hermes模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /hermes/hermes_agent)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/hermes/hermes_agent' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Hermes管理', 'HermesAgent', '/hermes/hermes_agent', 1, 'lucide:list', 1, '/hermes/hermes_agent/index', NULL, 1, 1, 1, '', 'Hermes Agent 表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = 'Hermes管理',
            name = 'HermesAgent',
            component = '/hermes/hermes_agent/index',
            remark = 'Hermes Agent 表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddHermesAgent', NULL, 1, NULL, 2, NULL, 'hermes:agent:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditHermesAgent', NULL, 2, NULL, 2, NULL, 'hermes:agent:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteHermesAgent', NULL, 3, NULL, 2, NULL, 'hermes:agent:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hermes:agent:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewHermesAgent', NULL, 4, NULL, 2, NULL, 'hermes:agent:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
