-- =====================================================
-- Lead管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-05-10 21:06:34.761216
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /lead_automation)
    SELECT id INTO v_parent_id FROM sys_menu
    WHERE path = '/lead_automation' AND type = 0
    ORDER BY id LIMIT 1;

    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Lead Automation', 'Lead_automation', '/lead_automation', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'lead_automation模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /lead_automation/lead_contact_source)
    SELECT id INTO v_menu_id FROM sys_menu
    WHERE path = '/lead_automation/lead_contact_source' AND type = 1
    ORDER BY id LIMIT 1;

    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Lead管理', 'LeadContactSource', '/lead_automation/lead_contact_source', 1, 'lucide:list', 1, '/lead_automation/lead_contact_source/index', NULL, 1, 1, 1, '', 'Lead multi-source evidence', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = 'Lead管理',
            name = 'LeadContactSource',
            component = '/lead_automation/lead_contact_source/index',
            remark = 'Lead multi-source evidence',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:contact:source:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddLeadContactSource', NULL, 1, NULL, 2, NULL, 'lead:contact:source:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:contact:source:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditLeadContactSource', NULL, 2, NULL, 2, NULL, 'lead:contact:source:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:contact:source:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteLeadContactSource', NULL, 3, NULL, 2, NULL, 'lead:contact:source:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:contact:source:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewLeadContactSource', NULL, 4, NULL, 2, NULL, 'lead:contact:source:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
