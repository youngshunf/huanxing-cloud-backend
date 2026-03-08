-- =====================================================
-- 内容阶段产出管理 菜单初始化 SQL (PostgreSQL)
-- 自动生成于: 2026-03-05 19:20:10.959884
-- 支持幂等操作：已存在则更新，不存在则新增
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- 查找或创建父级目录菜单 (path = /creator)
    SELECT id INTO v_parent_id FROM sys_menu 
    WHERE path = '/creator' AND type = 0
    ORDER BY id LIMIT 1;
    
    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('Creator', 'Creator', '/creator', 1, 'lucide:folder', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'creator模块', NULL, NOW(), NULL)
        RETURNING id INTO v_parent_id;
    END IF;

    -- 查找或创建主菜单 (path = /creator/hx_creator_content_stage)
    SELECT id INTO v_menu_id FROM sys_menu 
    WHERE path = '/creator/hx_creator_content_stage' AND type = 1
    ORDER BY id LIMIT 1;
    
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('内容阶段产出管理', 'HxCreatorContentStage', '/creator/hx_creator_content_stage', 1, 'lucide:list', 1, '/creator/hx_creator_content_stage/index', NULL, 1, 1, 1, '', '内容阶段产出表', v_parent_id, NOW(), NULL)
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET
            title = '内容阶段产出管理',
            name = 'HxCreatorContentStage',
            component = '/creator/hx_creator_content_stage/index',
            remark = '内容阶段产出表',
            parent_id = v_parent_id,
            updated_time = NOW()
        WHERE id = v_menu_id;
    END IF;

    -- 新增按钮（按 perms 判断）
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hx:creator:content:stage:add' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('新增', 'AddHxCreatorContentStage', NULL, 1, NULL, 2, NULL, 'hx:creator:content:stage:add', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 编辑按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hx:creator:content:stage:edit' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('编辑', 'EditHxCreatorContentStage', NULL, 2, NULL, 2, NULL, 'hx:creator:content:stage:edit', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 删除按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hx:creator:content:stage:del' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('删除', 'DeleteHxCreatorContentStage', NULL, 3, NULL, 2, NULL, 'hx:creator:content:stage:del', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;

    -- 查看按钮
    IF NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hx:creator:content:stage:get' AND parent_id = v_menu_id) THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
        VALUES ('查看', 'ViewHxCreatorContentStage', NULL, 4, NULL, 2, NULL, 'hx:creator:content:stage:get', 1, 0, 1, '', NULL, v_menu_id, NOW(), NULL);
    END IF;
END $$;

-- =====================================================
-- 菜单生成完成
-- =====================================================
