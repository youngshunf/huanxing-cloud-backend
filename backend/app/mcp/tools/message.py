"""
消息工具

提供消息发送和查询功能（简化版）
"""

from typing import Any

from backend.app.hasn.schema.hasn_message_hub import MessageHubSendRequest
from backend.app.hasn.service.hasn_message_hub_service import HasnMessageHubService
from backend.app.mcp.auth import AgentContext
from backend.app.mcp.tools.base import BaseTool
from backend.database.db import async_db_session


class MessageSendTool(BaseTool):
    """发送私信工具"""

    @property
    def source(self) -> str:
        return 'platform'

    @property
    def name(self) -> str:
        return 'hasn.message.send'

    @property
    def description(self) -> str:
        return '发送私信给指定用户或 Agent'

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'to': {'type': 'string', 'description': '接收者 HASN ID'},
                'content': {'type': 'string', 'description': '消息内容'},
            },
            'required': ['to', 'content'],
        }

    @property
    def required_scopes(self) -> list[str]:
        return ['message:write']

    async def execute(self, agent_context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        """执行工具"""
        # 维度① 能力授权已在 server.call_tool 按三态 mode 统一判定（D3 活取），
        # 工具内不再用凭证 scopes 快照二次校验（BUG2 空快照不应误拒）。
        missing_arguments = [name for name in ('to', 'content') if name not in arguments]
        if missing_arguments:
            raise RuntimeError(f'Missing required arguments: {", ".join(missing_arguments)}')

        # 使用消息服务发送消息
        async with async_db_session() as db:
            message_service = HasnMessageHubService()

            # 构造发送请求
            send_request = MessageHubSendRequest(
                from_hasn_id=agent_context.hasn_id,
                to_hasn_id=arguments['to'],
                content=arguments['content'],
                message_type='text',
            )

            # 发送消息
            result = await message_service.send_message(db, send_request)

            return {
                'success': True,
                'message_id': result.message_id if hasattr(result, 'message_id') else '',
                'from': agent_context.hasn_id,
                'to': arguments['to'],
                'status': 'sent',
            }


class MessageListTool(BaseTool):
    """获取消息列表工具（简化版）"""

    @property
    def source(self) -> str:
        return 'platform'

    @property
    def name(self) -> str:
        return 'hasn.message.list'

    @property
    def description(self) -> str:
        return '获取收件箱消息列表'

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
        """执行工具"""
        # 维度① 能力授权由 server.call_tool 三态 mode 统一判定（D3），工具内不二次校验。
        async with async_db_session() as db:
            message_service = HasnMessageHubService()

            # 获取收件箱消息
            # 注意：这里使用简化的实现，实际需要根据 API 调整
            try:
                from backend.app.hasn.schema.hasn_message_hub import InboxPullRequest

                pull_request = InboxPullRequest(hasn_id=agent_context.hasn_id, limit=arguments.get('limit', 20))

                result = await message_service.pull_inbox(db, pull_request)

                return {
                    'messages': [
                        {
                            'message_id': str(item.message_id),
                            'from': item.from_hasn_id,
                            'content': item.content if hasattr(item, 'content') else '',
                            'created_at': str(item.created_at) if hasattr(item, 'created_at') else '',
                        }
                        for item in result.items
                    ]
                    if hasattr(result, 'items')
                    else []
                }
            except Exception as e:
                # 如果 API 不匹配，返回友好错误
                return {'error': f'Message list not available: {e!s}', 'messages': []}
