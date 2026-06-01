"""端到端验证：真实 Agent 通过云端 MCP 发现并调用 community.create_post。

模拟真实 agent（安然）链路：
  - mint key 时 scopes=[]（证明授权不再依赖 key 快照，符合 D3）。
  L1: tools/list 应直接包含真实工具（含 hasn.community.create_post）。
  L2+L3: 默认 default_mode=allow → 直接调用 create_post 应 allow 并落库。
  L2-deny: 把 community:post 设为 deny（三态活取）→ 工具从 tools/list 消失 + 调用被拒；恢复。

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
    print(f'[mint] key id={pk}  (scopes=[] —— 故意不带 community:post)')

    try:
        # 基线：确保默认 allow
        await _set_mode('allow', {})

        headers = {'Authorization': f'Bearer {key}'}
        async with streamablehttp_client(MCP_URL, headers=headers) as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()

                # L1：tools/list 直接含真实工具
                tools = [t.name for t in (await session.list_tools()).tools]
                report['L1_tools_list'] = tools
                has_create = 'hasn.community.create_post' in tools
                print(f'\n[L1] tools/list({len(tools)}): {tools}')
                print(f'[L1] 包含 hasn.community.create_post? {"✅" if has_create else "❌"}')

                # L2+L3：默认 allow → 直接调用 create_post 应 allow + 落库
                allow_args = {
                    'content': '[E2E] 安然通过云端 MCP 发帖验证（默认 allow，key 无 community:post）。',
                    'visibility': 'public',
                }
                res_allow = _unwrap(
                    await session.call_tool('hasn.community.create_post', allow_args)
                )
                report['L2_allow_call'] = res_allow
                allow_payload = res_allow.get('payload') if isinstance(res_allow.get('payload'), dict) else {}
                dec = (allow_payload or {}).get('decision')
                pid = ((allow_payload or {}).get('result') or {}).get('post_id')
                allow_mark = '✅' if dec == 'allow' and pid else '❌'
                print(f'\n[L2+L3] 默认 allow 调用 create_post → decision={dec} post_id={pid} {allow_mark}')

                # L2-deny：把 community:post 设 deny（三态活取）→ 工具消失 + 调用被拒
                await _set_mode('allow', {'community:post': 'deny'})
                tools_after = [t.name for t in (await session.list_tools()).tools]
                gone = 'hasn.community.create_post' not in tools_after
                res_deny = _unwrap(
                    await session.call_tool('hasn.community.create_post', {'content': '[E2E] 应被 deny。'})
                )
                report['L2_deny_tools'] = tools_after
                report['L2_deny_call'] = res_deny
                deny_payload = res_deny.get('payload')
                deny_by_decision = isinstance(deny_payload, dict) and deny_payload.get('decision') == 'deny'
                denied = deny_by_decision or res_deny.get('is_error')
                gone_mark, deny_mark = ('✅' if gone else '❌'), ('✅' if denied else '❌')
                print(f'\n[L2-deny] 设 community:post=deny → 工具消失? {gone_mark} ; 调用被拒? {deny_mark}')
                print(f'         deny 返回: {json.dumps(deny_payload, ensure_ascii=False)[:160]}')
    finally:
        await _set_mode('allow', {})  # 恢复默认全开
        async with async_db_session() as db:
            await hasn_agent_mcp_keys_service.revoke(db, pk=pk, owner_hasn_id=OWNER_HASN)
            await db.commit()
        print(f'\n[cleanup] 已恢复安然三态为默认 allow + 吊销 key id={pk}')

    return report


if __name__ == '__main__':
    final_report = asyncio.run(main())
    with open('test-results/mcp_e2e_agent_post.json', 'w', encoding='utf-8') as fp:
        json.dump(final_report, fp, ensure_ascii=False, indent=2)
