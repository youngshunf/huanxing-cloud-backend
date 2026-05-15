"""
App Tool 动态注册

从应用平台动态加载和注册 App Tools
"""
import logging
from typing import Any

from backend.app.mcp.tools.base import BaseTool
from backend.app.mcp.context import AgentContext

logger = logging.getLogger(__name__)


class AppTool(BaseTool):
    """应用平台动态工具"""

    def __init__(
        self,
        installation_id: str,
        tool_name: str,
        tool_description: str,
        tool_input_schema: dict[str, Any],
        tool_required_scopes: list[str],
    ):
        self._installation_id = installation_id
        self._tool_name = tool_name
        self._tool_description = tool_description
        self._tool_input_schema = tool_input_schema
        self._tool_required_scopes = tool_required_scopes

    @property
    def name(self) -> str:
        """工具名称格式: app.{installation_id}.{tool_name}"""
        return f"app.{self._installation_id}.{self._tool_name}"

    @property
    def description(self) -> str:
        return self._tool_description

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._tool_input_schema

    @property
    def required_scopes(self) -> list[str]:
        return self._tool_required_scopes

    async def execute(
        self,
        agent_context: AgentContext,
        arguments: dict[str, Any],
    ) -> Any:
        """
        执行应用工具

        通过应用平台的 Tool API 网关调用
        """
        from backend.database.db_mysql import get_db
        from backend.app.app_platform.service.app_service import app_service
        from backend.app.app_platform.service.permission_validator import permission_validator

        async with get_db() as db:
            # 验证权限
            await permission_validator.check_installation_scopes(
                db=db,
                installation_id=self._installation_id,
                required_scopes=self._tool_required_scopes,
            )

            # 调用应用 Tool API
            result = await app_service.invoke_tool(
                db=db,
                installation_id=self._installation_id,
                tool_name=self._tool_name,
                input_data=arguments,
                actor_type="agent",
                actor_id=agent_context.hasn_id,
                owner_id=agent_context.owner_id,
            )

            return result


async def load_app_tools_for_agent(
    agent_id: str,
    owner_id: str,
) -> list[AppTool]:
    """
    为指定 Agent 加载所有可用的 App Tools

    Args:
        agent_id: Agent ID
        owner_id: Owner ID

    Returns:
        App Tools 列表
    """
    from backend.database.db_mysql import get_db
    from backend.app.app_platform.service.app_service import app_service

    tools = []

    async with get_db() as db:
        # 获取该 Agent 的所有安装
        installations = await app_service.list_installations_for_target(
            db=db,
            owner_id=owner_id,
            target_type="agent",
            target_id=agent_id,
        )

        for installation in installations:
            # 只加载 active 状态的安装
            if installation.status != "active":
                continue

            # 从 manifest 中提取 tools
            manifest = installation.manifest
            if not manifest or "tools" not in manifest:
                continue

            for tool_def in manifest["tools"]:
                try:
                    app_tool = AppTool(
                        installation_id=installation.installation_id,
                        tool_name=tool_def["name"],
                        tool_description=tool_def.get("description", ""),
                        tool_input_schema=tool_def.get("input_schema", {}),
                        tool_required_scopes=tool_def.get("required_scopes", []),
                    )
                    tools.append(app_tool)
                    logger.debug(
                        f"Loaded app tool: {app_tool.name} for agent {agent_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to load tool {tool_def.get('name')} "
                        f"from installation {installation.installation_id}: {e}"
                    )

    logger.info(f"Loaded {len(tools)} app tools for agent {agent_id}")
    return tools


async def load_app_tools_for_owner(owner_id: str) -> list[AppTool]:
    """
    为指定 Owner 加载所有可用的 App Tools

    Args:
        owner_id: Owner ID

    Returns:
        App Tools 列表
    """
    from backend.database.db_mysql import get_db
    from backend.app.app_platform.service.app_service import app_service

    tools = []

    async with get_db() as db:
        # 获取该 Owner 的所有安装
        installations = await app_service.list_installations_for_target(
            db=db,
            owner_id=owner_id,
            target_type="owner",
            target_id=owner_id,
        )

        for installation in installations:
            if installation.status != "active":
                continue

            manifest = installation.manifest
            if not manifest or "tools" not in manifest:
                continue

            for tool_def in manifest["tools"]:
                try:
                    app_tool = AppTool(
                        installation_id=installation.installation_id,
                        tool_name=tool_def["name"],
                        tool_description=tool_def.get("description", ""),
                        tool_input_schema=tool_def.get("input_schema", {}),
                        tool_required_scopes=tool_def.get("required_scopes", []),
                    )
                    tools.append(app_tool)
                except Exception as e:
                    logger.error(
                        f"Failed to load tool {tool_def.get('name')} "
                        f"from installation {installation.installation_id}: {e}"
                    )

    logger.info(f"Loaded {len(tools)} app tools for owner {owner_id}")
    return tools
