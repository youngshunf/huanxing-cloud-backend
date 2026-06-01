"""真实云端 MCP 联调 demo（零 mock）。

流程：
  1. 用后端 service 为真实 Agent「星诺」签发一把 Agent MCP Key（明文仅此一次）。
  2. 以真正的 MCP 客户端（streamable HTTP + JSON-RPC）连到运行中的云端后端
     http://127.0.0.1:8020/api/v1/mcp/streamable，Authorization: Bearer <key>。
  3. initialize → tools/list → 调用 hasn.contact.list / hasn.message.list /
     hasn.message.send（发给人类好友 + 已建立联系的好友 Agent）。
  4. 收尾吊销该 key。

不使用任何假数据：所有目标都是库里真实存在、且 message_router 判定可达的对象。
"""

import asyncio
import json

from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from sqlalchemy import text

from backend.app.hasn.schema.hasn_agent_mcp_keys import IssueAgentMcpKeyParam
from backend.app.hasn.service.hasn_agent_mcp_keys_service import hasn_agent_mcp_keys_service
from backend.database.db import async_db_session

MCP_URL = 'http://127.0.0.1:8020/api/v1/mcp/streamable'

SENDER_AGENT = 'a_cb5668f7-3a7e-416c-846b-bb771d68e9ec'  # 星诺 (assistant), owner 100001
OWNER_HASN = 'h_47094e96-ead5-4180-959a-8a28fac942e6'
HUMAN_FRIEND = 'h_411ee65b-0925-47b6-94b6-48e2cefbdcc1'  # 智小芽 100005
FRIEND_AGENT = 'a_5460a8db-74f8-4455-9e0b-5cd78976770b'  # 唤星默认 Agent 100004#assistant

MSG_TO_HUMAN = '你好智小芽，我是星诺，这是一条来自云端 MCP 工具的真实测试消息。'
MSG_TO_AGENT = '你好，我是星诺。通过云端 MCP 工具给已建立联系的好友 Agent 发条消息打个招呼。'


def _unwrap(result: Any) -> Any:
    """把 CallToolResult 的 content 解析成 Python 对象（JSON 文本→dict）。"""
    if result is None:
        return None
    is_error = getattr(result, 'isError', False)
    parts = []
    for item in getattr(result, 'content', []) or []:
        txt = getattr(item, 'text', None)
        if txt is None:
            parts.append(repr(item))
            continue
        try:
            parts.append(json.loads(txt))
        except (ValueError, TypeError):
            parts.append(txt)
    payload = parts[0] if len(parts) == 1 else parts
    return {'is_error': is_error, 'payload': payload}


async def mint_key() -> tuple[str, int]:
    async with async_db_session() as db:
        owner_user_id = (
            await db.execute(text('select user_id from hasn_humans where hasn_id=:h'), {'h': OWNER_HASN})
        ).scalar_one()
        issued = await hasn_agent_mcp_keys_service.issue(
            db,
            obj=IssueAgentMcpKeyParam(agent_hasn_id=SENDER_AGENT, scopes=[], node_id=None, expire_time=None),
            owner_hasn_id=OWNER_HASN,
            owner_user_id=int(owner_user_id),
        )
        await db.commit()
        return issued.key, issued.id


async def revoke_key(pk: int) -> None:
    async with async_db_session() as db:
        await hasn_agent_mcp_keys_service.revoke(db, pk=pk, owner_hasn_id=OWNER_HASN)
        await db.commit()


async def main() -> dict[str, Any]:
    report: dict[str, Any] = {'mcp_url': MCP_URL, 'sender_agent': SENDER_AGENT}

    key, pk = await mint_key()
    report['minted_key_prefix'] = key[:16] + '…'
    print(f'[mint] Agent MCP Key 已签发 id={pk} prefix={key[:16]}…')

    headers = {'Authorization': f'Bearer {key}'}
    try:
        async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _sid):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                report['server'] = {
                    'name': init.serverInfo.name,
                    'version': init.serverInfo.version,
                }
                print(f'[init] 连上云端 MCP: {init.serverInfo.name} v{init.serverInfo.version}')

                tools = await session.list_tools()
                report['tools'] = [t.name for t in tools.tools]
                print(f'[tools] 云端暴露 {len(tools.tools)} 个工具: {", ".join(report["tools"])}')

                print('\n[1] hasn.contact.list — 看联系人列表')
                report['contact_list'] = _unwrap(await session.call_tool('hasn.contact.list', {'limit': 50}))
                print(json.dumps(report['contact_list'], ensure_ascii=False, indent=2))

                print('\n[2] hasn.message.list — 查聊天记录（收件箱）')
                report['message_list'] = _unwrap(await session.call_tool('hasn.message.list', {'limit': 20}))
                print(json.dumps(report['message_list'], ensure_ascii=False, indent=2))

                print('\n[3] hasn.message.send → 人类好友 智小芽')
                report['send_to_human'] = _unwrap(
                    await session.call_tool('hasn.message.send', {'to': HUMAN_FRIEND, 'content': MSG_TO_HUMAN})
                )
                print(json.dumps(report['send_to_human'], ensure_ascii=False, indent=2))

                print('\n[4] hasn.message.send → 好友 Agent 唤星默认 Agent')
                report['send_to_agent'] = _unwrap(
                    await session.call_tool('hasn.message.send', {'to': FRIEND_AGENT, 'content': MSG_TO_AGENT})
                )
                print(json.dumps(report['send_to_agent'], ensure_ascii=False, indent=2))
    finally:
        await revoke_key(pk)
        print(f'\n[cleanup] 已吊销临时 key id={pk}')

    return report


if __name__ == '__main__':
    final_report = asyncio.run(main())
    with open('test-results/mcp_live_demo.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    print('\n[done] 报告已写入 test-results/mcp_live_demo.json')
