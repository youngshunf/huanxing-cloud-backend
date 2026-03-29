-- =====================================================
-- HASN 社交网络 - 统一菜单 SQL (PostgreSQL)
-- 清理并重建所有 HASN 模块菜单
-- =====================================================

DO $$
DECLARE
    v_parent_id INTEGER;
    v_menu_id INTEGER;
BEGIN
    -- ========================================
    -- 1. 创建顶级目录: HASN 社交网络
    -- ========================================
    SELECT id INTO v_parent_id FROM sys_menu
    WHERE path = '/hasn' AND type = 0
    ORDER BY id LIMIT 1;

    IF v_parent_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('HASN社交网络', 'Hasn', '/hasn', 80, 'lucide:network', 0, 'BasicLayout', NULL, 1, 1, 1, '', 'HASN 社交网络管理模块', NULL, NOW())
        RETURNING id INTO v_parent_id;
    ELSE
        UPDATE sys_menu SET title = 'HASN社交网络', icon = 'lucide:network', sort = 80 WHERE id = v_parent_id;
    END IF;

    -- ========================================
    -- 2. 用户管理
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_humans' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('用户管理', 'HasnHumans', '/hasn/hasn_humans', 1, 'lucide:users', 1, '/hasn/hasn_humans/index', NULL, 1, 1, 1, '', '人类用户身份管理', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '用户管理', icon = 'lucide:users', sort = 1, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    -- 按钮
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnHumans', NULL, 1, NULL, 2, 'hasn:humans:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:humans:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnHumans', NULL, 2, NULL, 2, 'hasn:humans:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:humans:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnHumans', NULL, 3, NULL, 2, 'hasn:humans:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:humans:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnHumans', NULL, 4, NULL, 2, 'hasn:humans:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:humans:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 3. Agent管理
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_agents' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('Agent管理', 'HasnAgents', '/hasn/hasn_agents', 2, 'lucide:bot', 1, '/hasn/hasn_agents/index', NULL, 1, 1, 1, '', 'AI Agent 管理', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = 'Agent管理', icon = 'lucide:bot', sort = 2, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnAgents', NULL, 1, NULL, 2, 'hasn:agents:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agents:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnAgents', NULL, 2, NULL, 2, 'hasn:agents:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agents:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnAgents', NULL, 3, NULL, 2, 'hasn:agents:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agents:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnAgents', NULL, 4, NULL, 2, 'hasn:agents:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agents:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 4. 客户端设备
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_clients' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('客户端设备', 'HasnClients', '/hasn/hasn_clients', 3, 'lucide:monitor-smartphone', 1, '/hasn/hasn_clients/index', NULL, 1, 1, 1, '', '客户端设备管理', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '客户端设备', icon = 'lucide:monitor-smartphone', sort = 3, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnClients', NULL, 1, NULL, 2, 'hasn:clients:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:clients:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnClients', NULL, 2, NULL, 2, 'hasn:clients:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:clients:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnClients', NULL, 3, NULL, 2, 'hasn:clients:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:clients:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnClients', NULL, 4, NULL, 2, 'hasn:clients:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:clients:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 5. 联系人关系
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_contacts' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('联系人管理', 'HasnContacts', '/hasn/hasn_contacts', 4, 'lucide:contact', 1, '/hasn/hasn_contacts/index', NULL, 1, 1, 1, '', '联系人关系（三维权限矩阵）', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '联系人管理', icon = 'lucide:contact', sort = 4, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnContacts', NULL, 1, NULL, 2, 'hasn:contacts:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:contacts:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnContacts', NULL, 2, NULL, 2, 'hasn:contacts:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:contacts:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnContacts', NULL, 3, NULL, 2, 'hasn:contacts:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:contacts:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnContacts', NULL, 4, NULL, 2, 'hasn:contacts:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:contacts:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 6. 会话管理
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_conversations' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('会话管理', 'HasnConversations', '/hasn/hasn_conversations', 5, 'lucide:messages-square', 1, '/hasn/hasn_conversations/index', NULL, 1, 1, 1, '', '单聊/群聊会话', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '会话管理', icon = 'lucide:messages-square', sort = 5, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnConversations', NULL, 1, NULL, 2, 'hasn:conversations:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:conversations:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnConversations', NULL, 2, NULL, 2, 'hasn:conversations:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:conversations:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnConversations', NULL, 3, NULL, 2, 'hasn:conversations:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:conversations:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnConversations', NULL, 4, NULL, 2, 'hasn:conversations:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:conversations:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 7. 消息管理
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_messages' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('消息管理', 'HasnMessages', '/hasn/hasn_messages', 6, 'lucide:mail', 1, '/hasn/hasn_messages/index', NULL, 1, 1, 1, '', '消息记录查询', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '消息管理', icon = 'lucide:mail', sort = 6, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnMessages', NULL, 1, NULL, 2, 'hasn:messages:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:messages:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnMessages', NULL, 2, NULL, 2, 'hasn:messages:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:messages:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnMessages', NULL, 3, NULL, 2, 'hasn:messages:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:messages:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnMessages', NULL, 4, NULL, 2, 'hasn:messages:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:messages:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 8. 群成员管理
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_group_members' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('群成员管理', 'HasnGroupMembers', '/hasn/hasn_group_members', 7, 'lucide:user-plus', 1, '/hasn/hasn_group_members/index', NULL, 1, 1, 1, '', '群聊成员管理', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '群成员管理', icon = 'lucide:user-plus', sort = 7, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnGroupMembers', NULL, 1, NULL, 2, 'hasn:group_members:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:group_members:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnGroupMembers', NULL, 2, NULL, 2, 'hasn:group_members:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:group_members:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnGroupMembers', NULL, 3, NULL, 2, 'hasn:group_members:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:group_members:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnGroupMembers', NULL, 4, NULL, 2, 'hasn:group_members:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:group_members:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 9. 未读计数
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_unread_counts' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('未读计数', 'HasnUnreadCounts', '/hasn/hasn_unread_counts', 8, 'lucide:bell-dot', 1, '/hasn/hasn_unread_counts/index', NULL, 1, 1, 1, '', '会话未读消息计数', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '未读计数', icon = 'lucide:bell-dot', sort = 8, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnUnreadCounts', NULL, 1, NULL, 2, 'hasn:unread_counts:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:unread_counts:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnUnreadCounts', NULL, 2, NULL, 2, 'hasn:unread_counts:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:unread_counts:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnUnreadCounts', NULL, 3, NULL, 2, 'hasn:unread_counts:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:unread_counts:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnUnreadCounts', NULL, 4, NULL, 2, 'hasn:unread_counts:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:unread_counts:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 10. Agent能力
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_agent_capabilities' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('Agent能力', 'HasnAgentCapabilities', '/hasn/hasn_agent_capabilities', 9, 'lucide:puzzle', 1, '/hasn/hasn_agent_capabilities/index', NULL, 1, 1, 1, '', 'Agent 能力声明', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = 'Agent能力', icon = 'lucide:puzzle', sort = 9, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnAgentCapabilities', NULL, 1, NULL, 2, 'hasn:agent_capabilities:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agent_capabilities:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnAgentCapabilities', NULL, 2, NULL, 2, 'hasn:agent_capabilities:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agent_capabilities:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnAgentCapabilities', NULL, 3, NULL, 2, 'hasn:agent_capabilities:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agent_capabilities:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnAgentCapabilities', NULL, 4, NULL, 2, 'hasn:agent_capabilities:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:agent_capabilities:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 11. 交易会话
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_trade_sessions' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('交易会话', 'HasnTradeSessions', '/hasn/hasn_trade_sessions', 10, 'lucide:handshake', 1, '/hasn/hasn_trade_sessions/index', NULL, 1, 1, 1, '', '商业/服务交易会话', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '交易会话', icon = 'lucide:handshake', sort = 10, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnTradeSessions', NULL, 1, NULL, 2, 'hasn:trade_sessions:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:trade_sessions:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnTradeSessions', NULL, 2, NULL, 2, 'hasn:trade_sessions:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:trade_sessions:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnTradeSessions', NULL, 3, NULL, 2, 'hasn:trade_sessions:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:trade_sessions:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnTradeSessions', NULL, 4, NULL, 2, 'hasn:trade_sessions:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:trade_sessions:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 12. 通知管理
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_notifications' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('通知管理', 'HasnNotifications', '/hasn/hasn_notifications', 11, 'lucide:bell-ring', 1, '/hasn/hasn_notifications/index', NULL, 1, 1, 1, '', '系统通知队列', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '通知管理', icon = 'lucide:bell-ring', sort = 11, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnNotifications', NULL, 1, NULL, 2, 'hasn:notifications:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:notifications:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnNotifications', NULL, 2, NULL, 2, 'hasn:notifications:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:notifications:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnNotifications', NULL, 3, NULL, 2, 'hasn:notifications:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:notifications:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnNotifications', NULL, 4, NULL, 2, 'hasn:notifications:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:notifications:get' AND parent_id = v_menu_id);

    -- ========================================
    -- 13. 审计日志
    -- ========================================
    SELECT id INTO v_menu_id FROM sys_menu WHERE path = '/hasn/hasn_audit_log' AND type = 1 ORDER BY id LIMIT 1;
    IF v_menu_id IS NULL THEN
        INSERT INTO sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time)
        VALUES ('审计日志', 'HasnAuditLog', '/hasn/hasn_audit_log', 12, 'lucide:shield-check', 1, '/hasn/hasn_audit_log/index', NULL, 1, 1, 1, '', '安全审计日志', v_parent_id, NOW())
        RETURNING id INTO v_menu_id;
    ELSE
        UPDATE sys_menu SET title = '审计日志', icon = 'lucide:shield-check', sort = 12, parent_id = v_parent_id WHERE id = v_menu_id;
    END IF;
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '新增', 'AddHasnAuditLog', NULL, 1, NULL, 2, 'hasn:audit_log:add', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:audit_log:add' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '编辑', 'EditHasnAuditLog', NULL, 2, NULL, 2, 'hasn:audit_log:edit', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:audit_log:edit' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '删除', 'DeleteHasnAuditLog', NULL, 3, NULL, 2, 'hasn:audit_log:del', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:audit_log:del' AND parent_id = v_menu_id);
    INSERT INTO sys_menu (title, name, path, sort, icon, type, perms, status, display, cache, link, parent_id, created_time) SELECT '查看', 'ViewHasnAuditLog', NULL, 4, NULL, 2, 'hasn:audit_log:get', 1, 0, 1, '', v_menu_id, NOW() WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE perms = 'hasn:audit_log:get' AND parent_id = v_menu_id);

END $$;

-- =====================================================
-- HASN 菜单导入完成
-- =====================================================
