-- =====================================================
-- 模板版本管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-05-26 20:57:28.089273
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /marketplace)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/marketplace' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Marketplace', 'Marketplace', '/marketplace', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'marketplace模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /marketplace/marketplace_template_version)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/marketplace/marketplace_template_version' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('模板版本管理', 'MarketplaceTemplateVersion', '/marketplace/marketplace_template_version', 1, 'lucide:list', 1, '/marketplace/marketplace_template_version/index', NULL, 1, 1, 1, '', '模板版本表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = '模板版本管理',
            name = 'MarketplaceTemplateVersion',
            component = '/marketplace/marketplace_template_version/index',
            remark = '模板版本表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'marketplace:template:version:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddMarketplaceTemplateVersion', NULL, 1, NULL, 2, NULL, 'marketplace:template:version:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'marketplace:template:version:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditMarketplaceTemplateVersion', NULL, 2, NULL, 2, NULL, 'marketplace:template:version:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'marketplace:template:version:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteMarketplaceTemplateVersion', NULL, 3, NULL, 2, NULL, 'marketplace:template:version:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'marketplace:template:version:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewMarketplaceTemplateVersion', NULL, 4, NULL, 2, NULL, 'marketplace:template:version:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
