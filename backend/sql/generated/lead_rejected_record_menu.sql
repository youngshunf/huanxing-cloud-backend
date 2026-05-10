-- =====================================================
-- Rejected,管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-05-10 21:06:34.996076
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

    -- 查找或创建主菜单 (path = /lead_automation/lead_rejected_record)
    SELECT id INTO v_menu_id FROM sys_menu
    WHERE path = '/lead_automation/lead_rejected_record' AND type = 1
    ORDER BY id LIMIT 1;

    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Rejected,管理', 'LeadRejectedRecord', '/lead_automation/lead_rejected_record', 1, 'lucide:list', 1, '/lead_automation/lead_rejected_record/index', NULL, 1, 1, 1, '', 'Rejected, invalid, duplicate, or failed lead record', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = 'Rejected,管理',
            name = 'LeadRejectedRecord',
            component = '/lead_automation/lead_rejected_record/index',
            remark = 'Rejected, invalid, duplicate, or failed lead record',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:rejected:record:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddLeadRejectedRecord', NULL, 1, NULL, 2, NULL, 'lead:rejected:record:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:rejected:record:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditLeadRejectedRecord', NULL, 2, NULL, 2, NULL, 'lead:rejected:record:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:rejected:record:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteLeadRejectedRecord', NULL, 3, NULL, 2, NULL, 'lead:rejected:record:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'lead:rejected:record:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewLeadRejectedRecord', NULL, 4, NULL, 2, NULL, 'lead:rejected:record:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
