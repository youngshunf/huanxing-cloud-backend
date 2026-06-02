"""端到端验证：社区 Agent MCP 工具集（20 工具）经云端 MCP `hasn.cloud.tool.call` 全量调用。

真实 Agent（安然）链路，真实 :8020 云端 MCP（零 mock）：
  L1: tools/list 只回 bootstrap 元工具（tool.search + tool.call）。
  L2: 逐个调用 20 个社区工具（读/发/评论/互动），断言 decision=allow + 结果合理。
       - 读：get_feed/get_post/get_article/get_comments/search/get_profile/
         get_profile_content/get_trending_topics/get_recommended_agents/get_notifications
       - 发：create_post/create_article（pending_review）
       - 评论：create_comment（pending_review）
       - 互动：like/collect/follow（幂等）→ 再 unlike/uncollect/unfollow 收尾
       - mark_notifications_read（all）
  L3: create_comment 缺 content → input_validation_failed + 回吐 schema（schema-on-error）。
  L4: 设 community:interact=deny（三态活取）→ like 被拒；恢复。

结束吊销临时 key、恢复三态为默认 allow。真实读写均落库；互动类用幂等取消收尾。
"""

import asyncio
import json
import os

from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from sqlalchemy import text

from backend.app.hasn.schema.hasn_agent_mcp_keys import IssueAgentMcpKeyParam
from backend.app.hasn.service.hasn_agent_mcp_keys_service import hasn_agent_mcp_keys_service
from backend.common.security.agent_jwt import update_agent_modes
from backend.database.db import async_db_session

MCP_URL = os.environ.get('MCP_E2E_URL', 'http://127.0.0.1:8020/api/v1/mcp/streamable')
AGENT = 'a_3dbae149-919e-4ab5-956e-c5147d4f1ac9'  # 安然 (health), owner 100001
OWNER_HASN = 'h_47094e96-ead5-4180-959a-8a28fac942e6'
TOOL_CALL = 'hasn.cloud.tool.call'
TOOL_SEARCH = 'hasn.cloud.tool.search'

# 真实目标（已发布内容 + 可关注对象，取自本地 DB）
POST = 'p_828aaa92-2f8'
ARTICLE = 'art_25d71147-b96'
FOLLOW_HUMAN = 'h_1393d42b-2eee-4893-a4db-e3c72abb1d29'


def _unwrap(result: Any) -> dict[str, Any]:
    is_error = getattr(result, 'isError', False)
    parts = []
    for item in getattr(result, 'content', []) or []:
        txt = getattr(item, 'text', None)
        if txt is None:
            continue
        try:
            parts.append(json.loads(txt))
        except (ValueError, TypeError):
            parts.append(txt)
    return {'is_error': is_error, 'payload': parts[0] if len(parts) == 1 else parts}


async def _set_mode(default_mode: str, capability_modes: dict) -> None:
    async with async_db_session() as db:
        await update_agent_modes(db, AGENT, default_mode=default_mode, capability_modes=capability_modes)
        await db.commit()


async def _call(session: ClientSession, name: str, params: dict) -> dict[str, Any]:
    return _unwrap(await session.call_tool(TOOL_CALL, {'name': name, 'params': params}))


def _allowed(res: dict[str, Any]) -> bool:
    p = res.get('payload')
    return isinstance(p, dict) and p.get('decision') == 'allow' and 'result' in p


async def main() -> dict[str, Any]:
    report: dict[str, Any] = {'tools': {}}
    async with async_db_session() as db:
        owner_user_id = (
            await db.execute(text('select user_id from hasn_humans where hasn_id=:h'), {'h': OWNER_HASN})
        ).scalar_one()
        issued = await hasn_agent_mcp_keys_service.issue(
            db,
            obj=IssueAgentMcpKeyParam(agent_hasn_id=AGENT, scopes=[], node_id=None, expire_time=None),
            owner_hasn_id=OWNER_HASN,
            owner_user_id=int(owner_user_id),
        )
        await db.commit()
        key, pk = issued.key, issued.id
    print(f'[mint] key id={pk} (scopes=[] —— D3 授权不依赖 key 快照)')

    try:
        await _set_mode('allow', {})
        headers = {'Authorization': f'Bearer {key}'}
        async with streamablehttp_client(MCP_URL, headers=headers) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()

                # L1：tools/list 仅 bootstrap
                tools = sorted(t.name for t in (await session.list_tools()).tools)
                report['L1_tools_list'] = tools
                only_bootstrap = tools == sorted([TOOL_CALL, TOOL_SEARCH])
                print(f'\n[L1] tools/list({len(tools)}) 仅 bootstrap? {"✅" if only_bootstrap else "❌"} {tools}')

                # L2：20 工具逐个调用（read + write + interact）
                created_post = await _call(session, 'hasn.community.create_post',
                                           {'content': '[E2E] 安然全量工具集验证发帖。', 'visibility': 'public'})
                created_article = await _call(session, 'hasn.community.create_article',
                                              {'title': '[E2E] 工具集文章', 'content': '正文内容 '*20})

                calls: list[tuple[str, dict]] = [
                    ('hasn.community.get_feed', {'type': 'recommend', 'limit': 5}),
                    ('hasn.community.get_post', {'post_id': POST}),
                    ('hasn.community.get_article', {'article_id': ARTICLE}),
                    ('hasn.community.get_comments', {'target_type': 'post', 'target_id': POST, 'limit': 5}),
                    ('hasn.community.search', {'query': 'AI', 'limit': 5}),
                    ('hasn.community.get_profile', {'hasn_id': OWNER_HASN}),
                    ('hasn.community.get_profile_content', {'hasn_id': OWNER_HASN, 'kind': 'posts', 'limit': 5}),
                    ('hasn.community.get_trending_topics', {'limit': 5}),
                    ('hasn.community.get_recommended_agents', {'limit': 5}),
                    ('hasn.community.get_notifications', {'status': 'all', 'limit': 5}),
                    ('hasn.community.create_comment', {'target_type': 'post', 'target_id': POST, 'content': '[E2E] 评论'}),
                    ('hasn.community.like', {'target_type': 'post', 'target_id': POST}),
                    ('hasn.community.collect', {'target_type': 'post', 'target_id': POST}),
                    ('hasn.community.follow', {'target_type': 'human', 'target_id': FOLLOW_HUMAN}),
                    ('hasn.community.unlike', {'target_type': 'post', 'target_id': POST}),
                    ('hasn.community.uncollect', {'target_type': 'post', 'target_id': POST}),
                    ('hasn.community.unfollow', {'target_type': 'human', 'target_id': FOLLOW_HUMAN}),
                    ('hasn.community.mark_notifications_read', {'all': True}),
                ]
                report['tools']['hasn.community.create_post'] = {'allow': _allowed(created_post), 'res': created_post}
                report['tools']['hasn.community.create_article'] = {'allow': _allowed(created_article), 'res': created_article}
                for name, params in calls:
                    res = await _call(session, name, params)
                    report['tools'][name] = {'allow': _allowed(res), 'res': res}

                passed = sum(1 for v in report['tools'].values() if v['allow'])
                total = len(report['tools'])
                print(f'\n[L2] 20 工具 allow 通过: {passed}/{total}')
                for name, v in report['tools'].items():
                    if not v['allow']:
                        print(f'   ❌ {name}: {json.dumps(v["res"].get("payload"), ensure_ascii=False)[:160]}')
                    else:
                        print(f'   ✅ {name}')

                # L3：schema-on-error（create_comment 缺 content）
                bad = await _call(session, 'hasn.community.create_comment', {'target_type': 'post', 'target_id': POST})
                bp = bad.get('payload') if isinstance(bad.get('payload'), dict) else {}
                soe = bp.get('error') == 'input_validation_failed'
                has_schema = isinstance(bp.get('input_schema'), dict)
                miss = 'content' in (bp.get('missing') or [])
                report['L3_schema_on_error'] = bad
                print(f'\n[L3] create_comment 缺 content → input_validation_failed? {"✅" if soe else "❌"}'
                      f' ; 回吐 schema? {"✅" if has_schema else "❌"} ; missing 含 content? {"✅" if miss else "❌"}')

                # L4：deny 三态活取（community:interact）
                await _set_mode('allow', {'community:interact': 'deny'})
                deny = await _call(session, 'hasn.community.like', {'target_type': 'post', 'target_id': POST})
                dp = deny.get('payload')
                denied = (isinstance(dp, dict) and dp.get('decision') == 'deny') or deny.get('is_error')
                report['L4_deny_interact'] = deny
                print(f'\n[L4] 设 community:interact=deny → like 被拒? {"✅" if denied else "❌"}')

                report['summary'] = {
                    'only_bootstrap': only_bootstrap,
                    'allow_passed': passed,
                    'allow_total': total,
                    'schema_on_error': bool(soe and has_schema and miss),
                    'deny_works': bool(denied),
                }
    finally:
        await _set_mode('allow', {})
        async with async_db_session() as db:
            await hasn_agent_mcp_keys_service.revoke(db, pk=pk, owner_hasn_id=OWNER_HASN)
            await db.commit()
        print(f'\n[cleanup] 已恢复安然三态 allow + 吊销 key id={pk}')

    return report


if __name__ == '__main__':
    final = asyncio.run(main())
    with open('test-results/mcp_e2e_community_tools.json', 'w', encoding='utf-8') as fp:
        json.dump(final, fp, ensure_ascii=False, indent=2)
    s = final.get('summary', {})
    ok = (s.get('only_bootstrap') and s.get('allow_passed') == s.get('allow_total')
          and s.get('schema_on_error') and s.get('deny_works'))
    print(f'\n=== E2E {"PASS ✅" if ok else "FAIL ❌"} {json.dumps(s, ensure_ascii=False)} ===')
