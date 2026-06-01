"""
平台消息工具（14-doc §2 能力 4/5）

hasn.message.send 走 message_router 真实路由（目标解析→关系/权限判决→会话→持久化→投递→
主人透明），替代旧 `hasn_messages_service.create` 裸插（G1）。维度②对象可达性由路由内
permission_engine 判定，工具返回 reachable/reason（不可达不静默成功），与维度①正交。
"""

from typing import Any

from backend.app.hasn.service import message_router
from backend.app.mcp.auth import AgentContext
from backend.app.mcp.tools.base import BaseTool
from backend.database.db import async_db_session


class MessageSendTool(BaseTool):
    """发送私信工具——走真实路由 + 关系门控 + 主人透明（G1）。"""

    @property
    def source(self) -> str:
        return 'platform'

    @property
    def name(self) -> str:
        return 'hasn.message.send'

    @property
    def namespace(self) -> str:
        return 'hasn.message'

    @property
    def description(self) -> str:
        return '给某用户/Agent/会话发消息（走真实路由：解析目标→关系权限→会话→投递→主人透明）'

    @property
    def risk_level(self) -> str:
        return 'low'

    @property
    def execution_location(self) -> str:
        return 'cloud'

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'to': {'type': 'string', 'description': '接收者 HASN ID / 唤星号 / 会话目标'},
                'content': {'type': 'string', 'description': '消息文本内容'},
                'content_type': {'type': 'string', 'enum': ['text'], 'description': '内容类型（默认 text）'},
            },
            'required': ['to', 'content'],
        }

    @property
    def required_scopes(self) -> list[str]:
        # G7：message:write → message:send（语义更准，14-doc §3）
        return ['message:send']

    async def execute(self, agent_context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        """走 message_router.route_message 真实投递；维度②可达性写进返回。

        维度① 能力授权已在 server.call_tool 按三态 mode 统一判定（D3），工具内不二次校验。
        """
        missing_arguments = [name for name in ('to', 'content') if name not in arguments]
        if missing_arguments:
            raise RuntimeError(f'Missing required arguments: {", ".join(missing_arguments)}')

        async with async_db_session() as db:
            # 身份取自 Agent 凭证（agent_hasn_id），不用 owner_user_id 冒名（G2）。
            result = await message_router.route_message(
                db=db,
                from_id=agent_context.agent_hasn_id,
                to_target=str(arguments['to']),
                content={'text': str(arguments['content'])},
                content_type=1,
                msg_type='message',
            )

        # 维度②：路由内 permission_engine（关系/信任）判决，不可达不静默成功。
        if result.get('error'):
            return {
                'message_id': None,
                'conversation_id': None,
                'delivered': False,
                'reachable': False,
                'reason': result.get('message', ''),
                'code': result.get('code'),
            }

        status = result.get('status')
        # CONFIRM 决策（如需主人确认）→ 已挂起，未送达但目标可达
        if status == 'pending_confirmation':
            return {
                'message_id': None,
                'conversation_id': result.get('conversation_id'),
                'delivered': False,
                'reachable': True,
                'status': status,
                'reason': result.get('reason', ''),
            }
        return {
            'message_id': result.get('msg_id'),
            'conversation_id': result.get('conversation_id'),
            'delivered': status == 'sent',
            'reachable': True,
            'status': status,
        }


def _extract_text(envelope: dict[str, Any]) -> str:
    """从 HASN envelope 里尽力取出可读文本（content 可能是 dict 或 str）。"""
    content = envelope.get('content')
    if isinstance(content, dict):
        return str(content.get('text') or content.get('content') or '')
    if isinstance(content, str):
        return content
    return ''


def _extract_sender(envelope: dict[str, Any]) -> str:
    """从 envelope 取出发送方 hasn_id（兼容多种字段命名）。"""
    routing = envelope.get('routing') if isinstance(envelope.get('routing'), dict) else {}
    return str(
        envelope.get('from')
        or envelope.get('from_hasn_id')
        or envelope.get('sender_hasn_id')
        or routing.get('from')
        or ''
    )


class MessageListTool(BaseTool):
    """获取主人收件箱消息列表（含主人透明副本）。"""

    @property
    def source(self) -> str:
        return 'platform'

    @property
    def name(self) -> str:
        return 'hasn.message.list'

    @property
    def namespace(self) -> str:
        return 'hasn.message'

    @property
    def execution_location(self) -> str:
        return 'cloud'

    @property
    def description(self) -> str:
        return '获取收件箱消息列表（最近的会话消息，含发送方/文本/会话/时间）'

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'description': '返回数量限制（默认 20）', 'minimum': 1, 'maximum': 100}
            },
        }

    @property
    def required_scopes(self) -> list[str]:
        return ['message:read']

    async def execute(self, agent_context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        # 维度① 能力授权由 server.call_tool 三态 mode 统一判定（D3），工具内不二次校验。
        from backend.app.hasn.schema.hasn_message_hub import InboxPullRequest
        from backend.app.hasn.service.hasn_message_hub_service import HasnMessageHubService

        limit = min(max(int(arguments.get('limit', 20)), 1), 100)
        async with async_db_session() as db:
            message_service = HasnMessageHubService()
            # 收件箱按 owner 维度拉取（主人透明：含 Agent 会话的 owner_copy）。
            pull_request = InboxPullRequest(owner_id=agent_context.owner_hasn_id)
            result = await message_service.pull_inbox(db, pull_request)

            messages = []
            for item in result.items[:limit]:
                envelope = item.envelope or {}
                messages.append({
                    'message_id': str(item.message_id),
                    'conversation_id': str(item.conversation_id),
                    'inbox_kind': getattr(item.inbox_kind, 'value', item.inbox_kind),
                    'from': _extract_sender(envelope),
                    'content': _extract_text(envelope),
                    'created_at': str(item.created_at),
                })
            return {'messages': messages, 'has_more': result.has_more, 'next_cursor': result.next_cursor}
