"""
联系人工具

提供联系人查询功能（简化版）
"""
from typing import Any

from backend.app.hasn.service.hasn_contacts_service import HasnContactsService
from backend.app.mcp.auth import AgentContext
from backend.app.mcp.tools.base import BaseTool
from backend.database.db import async_db_session


class ContactListTool(BaseTool):
    """获取联系人列表工具"""

    @property
    def source(self) -> str:
        return "platform"

    @property
    def name(self) -> str:
        return "hasn.contact.list"

    @property
    def description(self) -> str:
        return "获取联系人列表"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "返回数量限制（默认 50）",
                    "minimum": 1,
                    "maximum": 100
                }
            }
        }

    @property
    def required_scopes(self) -> list[str]:
        return ["contact:read"]

    async def execute(
        self,
        agent_context: AgentContext,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """执行工具"""
        # 检查权限
        agent_context.require_scopes("contact:read")

        async with async_db_session() as db:
            contact_service = HasnContactsService()

            # 获取联系人列表
            try:
                result = await contact_service.get_list(
                    db=db,
                    user_id=agent_context.owner_id
                )

                # 提取联系人数据
                contacts = result.get("data", []) if isinstance(result, dict) else []

                return {
                    "contacts": [
                        {
                            "contact_id": contact.id if hasattr(contact, 'id') else "",
                            "contact_hasn_id": contact.contact_id if hasattr(contact, 'contact_id') else "",
                            "status": contact.status if hasattr(contact, 'status') else "active",
                            "created_at": str(contact.created_at) if hasattr(contact, 'created_at') else ""
                        }
                        for contact in contacts
                    ]
                }
            except Exception as e:
                return {
                    "error": f"Failed to list contacts: {e!s}",
                    "contacts": []
                }
