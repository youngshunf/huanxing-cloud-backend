"""端到端验证：渐进式暴露 + 元工具 tool.call + schema-on-error（设计 03 §9）。

真实 Agent（安然）链路，真实 :8020 云端 MCP：
  L1: tools/list 只回 bootstrap 元工具（tool.search + tool.call）；长尾 create_post 不在清单。
  L2: tool.call('hasn.community.create_post', 合法 params) → 落库（decision=allow + post_id）。
  L3: tool.call(create_post, 缺 content) → input_validation_failed + 回吐内层完整 schema；
      据 schema 补正 content 后重试 → 落库（schema-on-error 自纠）。
  L4: 设 community:post=deny（三态活取）→ tool.call(create_post) 被拒；恢复。

结束吊销临时 key、恢复三态为默认 allow。
"""

import asyncio
import json

from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from sqlalchemy import text

from backend.app.hasn.schema.hasn_agent_mcp_keys import IssueAgentMcpKeyParam
from backend.app.hasn.service.hasn_agent_mcp_keys_service import hasn_agent_mcp_keys_service
from backend.common.security.agent_jwt import update_agent_modes
from backend.database.db import async_db_session

MCP_URL = 'http://127.0.0.1:8020/api/v1/mcp/streamable'
AGENT = 'a_3dbae149-919e-4ab5-956e-c5147d4f1ac9'  # 安然 (health), owner 100001
OWNER_HASN = 'h_47094e96-ead5-4180-959a-8a28fac942e6'
CREATE_POST = 'hasn.community.create_post'
TOOL_CALL = 'hasn.cloud.tool.call'


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


async def _call_via_meta(session: ClientSession, name: str, params: dict) -> dict[str, Any]:
    """经元工具 tool.call 转发调用内层工具。"""
    return _unwrap(await session.call_tool(TOOL_CALL, {'name': name, 'params': params}))


async def main() -> dict[str, Any]:
    report: dict[str, Any] = {}
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
    print(f'[mint] key id={pk}  (scopes=[] —— D3 授权不依赖 key 快照)')

    try:
        await _set_mode('allow', {})  # 基线默认全开
        headers = {'Authorization': f'Bearer {key}'}
        async with streamablehttp_client(MCP_URL, headers=headers) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()

                # L1：tools/list 只回 bootstrap 元工具
                tools = sorted(t.name for t in (await session.list_tools()).tools)
                report['L1_tools_list'] = tools
                only_bootstrap = tools == [TOOL_CALL, 'hasn.cloud.tool.search']
                print(f'\n[L1] tools/list({len(tools)}): {tools}')
                print(f'[L1] 仅 bootstrap 元工具 + create_post 不在清单? {"✅" if only_bootstrap else "❌"}')

                # L2：tool.call 合法直调 → 落库
                valid = {
                    'content': '[E2E] 安然经 tool.call 元工具发帖（渐进式暴露 + 直调）。',
                    'visibility': 'public',
                }
                res_ok = await _call_via_meta(session, CREATE_POST, valid)
                report['L2_meta_call'] = res_ok
                ok_payload = res_ok.get('payload') if isinstance(res_ok.get('payload'), dict) else {}
                dec = (ok_payload or {}).get('decision')
                pid = ((ok_payload or {}).get('result') or {}).get('post_id')
                l2_mark = '✅' if dec == 'allow' and pid else '❌'
                print(f'\n[L2] tool.call(create_post, 合法) → decision={dec} post_id={pid} {l2_mark}')

                # L3：缺 content → schema-on-error 回吐 schema；补正后重试落库
                res_bad = await _call_via_meta(session, CREATE_POST, {'visibility': 'public'})
                bad_payload = res_bad.get('payload') if isinstance(res_bad.get('payload'), dict) else {}
                is_soe = bad_payload.get('error') == 'input_validation_failed'
                has_schema = isinstance(bad_payload.get('input_schema'), dict)
                missing_content = 'content' in (bad_payload.get('missing') or [])
                report['L3_schema_on_error'] = res_bad
                soe_m, sch_m, mc_m = (
                    '✅' if is_soe else '❌',
                    '✅' if has_schema else '❌',
                    '✅' if missing_content else '❌',
                )
                print(f'\n[L3] tool.call(create_post, 缺content) → input_validation_failed? {soe_m}'
                      f' ; 回吐 schema? {sch_m} ; missing 含 content? {mc_m}')

                # 据回吐 schema 补正 content 后重试
                fixed = {'content': '[E2E] schema-on-error 自纠后重试发帖。', 'visibility': 'public'}
                res_retry = await _call_via_meta(session, CREATE_POST, fixed)
                retry_payload = res_retry.get('payload') if isinstance(res_retry.get('payload'), dict) else {}
                retry_pid = ((retry_payload or {}).get('result') or {}).get('post_id')
                report['L3_retry'] = res_retry
                print(f'[L3] 补正后重试 → decision={(retry_payload or {}).get("decision")} post_id={retry_pid}'
                      f' {"✅" if retry_pid else "❌"}')

                # L4：deny 三态活取 → tool.call 被拒
                await _set_mode('allow', {'community:post': 'deny'})
                res_deny = await _call_via_meta(session, CREATE_POST, valid)
                deny_payload = res_deny.get('payload')
                deny_by_decision = isinstance(deny_payload, dict) and deny_payload.get('decision') == 'deny'
                denied = deny_by_decision or res_deny.get('is_error')
                report['L4_deny_call'] = res_deny
                print(f'\n[L4] 设 community:post=deny → tool.call(create_post) 被拒? {"✅" if denied else "❌"}')
    finally:
        await _set_mode('allow', {})
        async with async_db_session() as db:
            await hasn_agent_mcp_keys_service.revoke(db, pk=pk, owner_hasn_id=OWNER_HASN)
            await db.commit()
        print(f'\n[cleanup] 已恢复安然三态为默认 allow + 吊销 key id={pk}')

    return report


if __name__ == '__main__':
    final_report = asyncio.run(main())
    with open('test-results/mcp_e2e_tool_call.json', 'w', encoding='utf-8') as fp:
        json.dump(final_report, fp, ensure_ascii=False, indent=2)
    print('\n=== 写入 test-results/mcp_e2e_tool_call.json ===')
