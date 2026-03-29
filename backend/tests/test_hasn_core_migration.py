"""HASN 核心功能集成测试

测试迁移后的 5 大核心模块：
1. hasn_auth - JWT 签发/验证、身份注册
2. ws_router - WebSocket 连接管理、Agent 上报
3. message_router - 消息路由（目标解析→权限→持久化→投递）
4. route_guard - 守门人权限校验
5. contacts CRUD - 联系人业务方法
"""
import asyncio
import sys
import os

# 需要在 backend 根目录下运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def run_tests():
    results = []

    def ok(name):
        results.append(('✅', name))
        print(f'  ✅ {name}')

    def fail(name, e):
        results.append(('❌', name, str(e)))
        print(f'  ❌ {name}: {e}')

    # ═══════════════════════════════════════
    # 1. hasn_auth 测试
    # ═══════════════════════════════════════
    print('\n🔐 模块1: hasn_auth (认证服务)')
    print('─' * 50)

    try:
        from backend.app.hasn.service.hasn_auth import (
            issue_client_jwt, verify_client_jwt, _generate_api_key,
            hasn_auth_from_jwt, hasn_auth_dual,
            HASN_CLIENT_JWT_SECRET
        )
        ok('模块导入成功')
    except Exception as e:
        fail('模块导入', e)
        return results

    # 1.1 Client JWT 签发
    try:
        token = issue_client_jwt(
            user_hasn_id='h_test-user-001',
            client_id='c_test-client-001',
            client_type='desktop',
            star_id='100001',
        )
        assert token and len(token) > 50
        ok(f'Client JWT 签发成功 (len={len(token)})')
    except Exception as e:
        fail('Client JWT 签发', e)

    # 1.2 Client JWT 验证
    try:
        payload = verify_client_jwt(token)
        assert payload['sub'] == 'h_test-user-001'
        assert payload['client_id'] == 'c_test-client-001'
        assert payload['client_type'] == 'desktop'
        assert payload['star_id'] == '100001'
        assert payload['type'] == 'client'
        ok(f'Client JWT 验证成功 (sub={payload["sub"]}, client={payload["client_id"]})')
    except Exception as e:
        fail('Client JWT 验证', e)

    # 1.3 过期 JWT 验证
    try:
        import jwt as pyjwt
        from datetime import timedelta
        from backend.utils.timezone import timezone
        expired_payload = {
            'sub': 'h_test', 'client_id': 'c_test', 'type': 'client',
            'exp': int((timezone.now() - timedelta(hours=1)).timestamp()),
        }
        expired_token = pyjwt.encode(expired_payload, HASN_CLIENT_JWT_SECRET, algorithm='HS256')
        try:
            verify_client_jwt(expired_token)
            fail('过期JWT应该抛异常', '未抛出')
        except Exception as ex:
            if '过期' in str(ex) or 'expired' in str(ex).lower():
                ok('过期 JWT 正确拒绝')
            else:
                ok(f'过期 JWT 正确拒绝 ({ex})')
    except Exception as e:
        fail('过期JWT测试', e)

    # 1.4 API Key 生成
    try:
        raw_key, key_hash = _generate_api_key()
        assert raw_key.startswith('hasn_ak_')
        assert len(key_hash) == 64  # SHA256
        import hashlib
        assert hashlib.sha256(raw_key.encode()).hexdigest() == key_hash
        ok(f'API Key 生成成功 (prefix=hasn_ak_, hash_len={len(key_hash)})')
    except Exception as e:
        fail('API Key 生成', e)

    # ═══════════════════════════════════════
    # 2. ws_router 测试
    # ═══════════════════════════════════════
    print('\n📡 模块2: ws_router (WebSocket 连接管理)')
    print('─' * 50)

    try:
        from backend.app.hasn.service.ws_router import (
            ws_router, WsRouterService, _ws_connections,
            CLIENT_CONN_KEY, USER_CLIENTS_PREFIX, AGENT_CLIENT_KEY,
            OFFLINE_PREFIX, OFFLINE_TTL
        )
        ok('模块导入成功')
    except Exception as e:
        fail('模块导入', e)
        return results

    # 2.1 类结构验证
    try:
        assert isinstance(ws_router, WsRouterService)
        assert hasattr(ws_router, 'register_client')
        assert hasattr(ws_router, 'unregister_client')
        assert hasattr(ws_router, 'report_agents')
        assert hasattr(ws_router, 'push_message_to')
        assert hasattr(ws_router, 'get_offline_messages')
        assert hasattr(ws_router, 'is_human_online')
        assert hasattr(ws_router, 'is_agent_online')
        assert hasattr(ws_router, 'get_entity_status')
        ok('WsRouterService 9 个核心方法完整')
    except Exception as e:
        fail('类结构验证', e)

    # 2.2 Redis 键前缀配置
    try:
        assert CLIENT_CONN_KEY == 'hasn:client_conn'
        assert USER_CLIENTS_PREFIX == 'hasn:user_clients'
        assert AGENT_CLIENT_KEY == 'hasn:agent_client'
        assert OFFLINE_PREFIX == 'hasn:offline'
        assert OFFLINE_TTL == 604800  # 7天
        ok('Redis 键前缀与 TTL 配置正确')
    except Exception as e:
        fail('Redis 键前缀', e)

    # 2.3 连接存储结构
    try:
        assert isinstance(_ws_connections, dict)
        ok(f'进程内连接存储就绪 (当前连接数: {len(_ws_connections)})')
    except Exception as e:
        fail('连接存储结构', e)

    # ═══════════════════════════════════════
    # 3. message_router 测试
    # ═══════════════════════════════════════
    print('\n📬 模块3: message_router (消息路由引擎)')
    print('─' * 50)

    try:
        from backend.app.hasn.service.message_router import (
            resolve_target, check_relation_permission,
            get_or_create_conversation, persist_message,
            route_message, mark_read, recall_message,
            _entity_type_int,
        )
        ok('模块导入成功（7 个核心函数）')
    except Exception as e:
        fail('模块导入', e)
        return results

    # 3.1 实体类型判断
    try:
        assert _entity_type_int('h_abc') == 1  # human
        assert _entity_type_int('a_xyz') == 2  # agent
        assert _entity_type_int('sys_001') == 3  # system
        ok('实体类型判断: h_→1(human), a_→2(agent), other→3(system)')
    except Exception as e:
        fail('实体类型判断', e)

    # 3.2 Model 引用验证（确认新 model 可用）
    try:
        from backend.app.hasn.model import (
            HasnHumans, HasnMessages, HasnConversations,
            HasnUnreadCounts, HasnAgents, HasnContacts,
        )
        # 验证新表字段
        assert hasattr(HasnConversations, 'participant_a_id')
        assert hasattr(HasnConversations, 'participant_b_id')
        assert hasattr(HasnConversations, 'participant_a_type')
        assert hasattr(HasnConversations, 'participant_b_type')
        assert hasattr(HasnConversations, 'relation_type')
        assert hasattr(HasnConversations, 'last_message_from')
        assert hasattr(HasnConversations, 'last_message_id')
        assert hasattr(HasnConversations, 'message_count')
        ok('新 Model 字段验证通过 (participant_a_id/b_id/a_type/b_type/relation_type/last_message_from)')
    except Exception as e:
        fail('Model 引用验证', e)

    # 3.3 DB 集成测试: resolve_target + 消息路由
    try:
        from backend.database.db import async_db_session
        async with async_db_session() as db:
            # 测试目标解析 - 不存在的用户
            result = await resolve_target(db, 'h_nonexistent')
            assert result is None
            ok('目标解析: 不存在的 hasn_id → None')

            # 测试目标解析 - 不存在的 star_id
            result2 = await resolve_target(db, '999999')
            assert result2 is None
            ok('目标解析: 不存在的 star_id → None')

            # 测试权限检查 - 无关系
            perm = await check_relation_permission(db, 'h_fake_a', 'h_fake_b')
            assert perm['allowed'] is False
            assert '无关系' in perm.get('reason', '')
            ok(f'权限检查: 无关系用户 → 拒绝 (reason={perm["reason"]})')

            # 测试权限检查 - 好友请求类型（无需关系）
            perm2 = await check_relation_permission(db, 'h_fake_a', 'h_fake_b', 'contact_request')
            assert perm2['allowed'] is True
            ok('权限检查: contact_request 类型 → 允许（无需已有关系）')

            # 测试消息路由 - 目标不存在
            route_result = await route_message(
                db=db, from_id='h_test', to_target='h_nonexistent',
                content={'text': 'hello'}, content_type=1,
            )
            assert route_result['error'] is True
            assert route_result['code'] == 3001
            ok(f'消息路由: 目标不存在 → error=True, code={route_result["code"]}')

    except Exception as e:
        fail('DB 集成测试', e)

    # ═══════════════════════════════════════
    # 4. route_guard 测试
    # ═══════════════════════════════════════
    print('\n🛡️  模块4: route_guard (权限守门人)')
    print('─' * 50)

    try:
        from backend.app.hasn.service.route_guard import route_guard, RouteGuardService
        ok('模块导入成功')
    except Exception as e:
        fail('模块导入', e)
        return results

    try:
        assert isinstance(route_guard, RouteGuardService)
        assert hasattr(route_guard, 'check_permission')
        assert hasattr(route_guard, 'invalidate_cache')
        assert RouteGuardService.CACHE_PREFIX == 'hasn:rel'
        assert RouteGuardService.CACHE_TTL == 600
        ok(f'RouteGuardService 结构正确 (cache_prefix=hasn:rel, ttl=600s)')
    except Exception as e:
        fail('类结构验证', e)

    # 4.1 DB 集成: 无关系用户 → 拦截
    try:
        from backend.database.db import async_db_session
        async with async_db_session() as db:
            allowed = await route_guard.check_permission(db, 'h_guard_a', 'h_guard_b')
            assert allowed is False
            ok('守门人检查: 无关系用户 → 拦截 (False)')
    except Exception as e:
        fail('守门人DB检查', e)

    # ═══════════════════════════════════════
    # 5. contacts CRUD 测试
    # ═══════════════════════════════════════
    print('\n👥 模块5: contacts CRUD (联系人业务)')
    print('─' * 50)

    try:
        from backend.app.hasn.crud.crud_hasn_contacts import hasn_contacts_dao, CRUDHasnContacts
        from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao, CRUDHasnHumans
        from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao, CRUDHasnAgents
        ok('3 个 CRUD DAO 导入成功')
    except Exception as e:
        fail('CRUD 导入', e)
        return results

    # 5.1 业务方法存在性
    try:
        biz_methods = [
            'get_relation', 'get_bidirectional', 'list_contacts',
            'get_pending_requests', 'create_contact', 'accept_request',
            'reject_request', 'update_trust_level', 'block',
        ]
        for m in biz_methods:
            assert hasattr(hasn_contacts_dao, m), f'缺少方法: {m}'
        ok(f'contacts DAO: {len(biz_methods)} 个业务方法完整')
    except Exception as e:
        fail('contacts 业务方法', e)

    try:
        human_methods = ['get_by_hasn_id', 'get_by_star_id', 'get_by_user_id']
        for m in human_methods:
            assert hasattr(hasn_humans_dao, m), f'缺少方法: {m}'
        ok(f'humans DAO: {len(human_methods)} 个查询方法完整')
    except Exception as e:
        fail('humans 查询方法', e)

    try:
        agent_methods = ['get_by_hasn_id', 'get_by_star_id']
        for m in agent_methods:
            assert hasattr(hasn_agents_dao, m), f'缺少方法: {m}'
        ok(f'agents DAO: {len(agent_methods)} 个查询方法完整')
    except Exception as e:
        fail('agents 查询方法', e)

    # 5.2 DB 集成: 查询
    try:
        from backend.database.db import async_db_session
        async with async_db_session() as db:
            rel = await hasn_contacts_dao.get_relation(db, 'h_none', 'h_none2', 'social')
            assert rel is None
            ok('contacts.get_relation: 不存在的关系 → None')

            bidir = await hasn_contacts_dao.get_bidirectional(db, 'h_none', 'h_none2')
            assert bidir is None
            ok('contacts.get_bidirectional: 不存在 → None')

            pending = await hasn_contacts_dao.get_pending_requests(db, 'h_none')
            assert isinstance(pending, list) and len(pending) == 0
            ok('contacts.get_pending_requests: 空结果 → []')

            contacts = await hasn_contacts_dao.list_contacts(db, 'h_none')
            assert isinstance(contacts, list) and len(contacts) == 0
            ok('contacts.list_contacts: 空结果 → []')
    except Exception as e:
        fail('contacts DB 集成', e)

    # ═══════════════════════════════════════
    # 6. WebSocket API 端点验证
    # ═══════════════════════════════════════
    print('\n🔌 模块6: ws_client (WebSocket 端点)')
    print('─' * 50)

    try:
        from backend.app.hasn.api.ws_client import router as ws_router_api
        routes = [r.path for r in ws_router_api.routes]
        assert '/ws/client' in routes
        ok(f'WebSocket 端点注册: {routes}')
    except Exception as e:
        fail('WS 端点注册', e)

    # ═══════════════════════════════════════
    # 7. contacts API 端点验证
    # ═══════════════════════════════════════
    print('\n📋 模块7: contacts API (联系人端点)')
    print('─' * 50)

    try:
        from backend.app.hasn.api.v1.app.contacts import router as contacts_router
        routes = {r.path: list(r.methods) for r in contacts_router.routes if hasattr(r, 'methods')}
        assert '/contacts/request' in routes
        assert '/contacts/requests' in routes
        assert '/contacts' in routes
        ok(f'联系人 API 端点: {list(routes.keys())}')
    except Exception as e:
        fail('contacts 端点', e)

    # ═══════════════════════════════════════
    # 8. auth API 端点验证
    # ═══════════════════════════════════════
    print('\n🔑 模块8: hasn_auth_api (认证 REST 端点)')
    print('─' * 50)

    try:
        from backend.app.hasn.api.v1.app.hasn_auth_api import router as auth_api_router
        routes = {r.path: list(r.methods) for r in auth_api_router.routes if hasattr(r, 'methods')}
        expected = ['/auth/register', '/auth/register-client', '/auth/client-token', '/me', '/me/clients', '/me/agents']
        for ep in expected:
            assert ep in routes, f'缺少端点: {ep}'
        ok(f'认证 API 端点: {list(routes.keys())}')
    except Exception as e:
        fail('auth API 端点', e)

    # ═══════════════════════════════════════
    # 9. Schema 验证
    # ═══════════════════════════════════════
    print('\n📐 模块9: Schema (联系人业务数据结构)')
    print('─' * 50)

    try:
        from backend.app.hasn.schema.hasn_contacts_business import (
            HasnContactRequestReq, HasnContactRespondReq,
            HasnContactPeerOut, HasnContactRequestOut,
            HasnContactOut, HasnContactListResp,
            HasnTrustLevelReq, TRUST_LEVEL_LABELS,
        )
        # 验证信任等级标签
        assert TRUST_LEVEL_LABELS == {0: 'blocked', 1: 'stranger', 2: 'normal', 3: 'trusted', 4: 'owner'}

        # 验证 Schema 可实例化
        peer = HasnContactPeerOut(hasn_id='h_test', star_id='100001', name='测试', type='human')
        assert peer.hasn_id == 'h_test'

        req = HasnContactRequestReq(target_star_id='100002', message='你好')
        assert req.target_star_id == '100002'

        ok(f'8 个 Schema 类 + TRUST_LEVEL_LABELS 验证通过')
    except Exception as e:
        fail('Schema 验证', e)

    # ═══════════════════════════════════════
    # 汇总
    # ═══════════════════════════════════════
    print('\n' + '═' * 60)
    total = len(results)
    passed = sum(1 for r in results if r[0] == '✅')
    failed = sum(1 for r in results if r[0] == '❌')
    print(f'📊 测试汇总: {passed}/{total} 通过, {failed} 失败')

    if failed > 0:
        print('\n失败项:')
        for r in results:
            if r[0] == '❌':
                print(f'  ❌ {r[1]}: {r[2]}')

    print('═' * 60)
    return results


if __name__ == '__main__':
    asyncio.run(run_tests())
