"""
App Tool 动态注册

从应用平台动态加载和注册 App Tools
"""
from __future__ import annotations

import logging

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from backend.app.app_platform.crud.crud_app_agent_bindings import app_agent_bindings_dao
from backend.app.app_platform.crud.crud_app_installations import app_installations_dao
from backend.app.app_platform.crud.crud_app_manifests import app_manifests_dao
from backend.app.app_platform.crud.crud_app_tools import app_tools_dao
from backend.app.app_platform.crud.crud_app_versions import app_versions_dao
from backend.app.app_platform.service.runtime_gateway import runtime_gateway
from backend.app.mcp.tools.base import BaseTool
from backend.database.db import async_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.mcp.context import AgentContext

logger = logging.getLogger(__name__)


class AppTool(BaseTool):
    """应用平台动态工具"""

    def __init__(
        self,
        installation_id: str,
        app_id: str,
        app_namespace: str,
        tool_id: str,
        tool_name: str,
        tool_description: str,
        tool_input_schema: dict[str, Any],
        tool_required_scopes: list[str],
        action: str | None = None,
        tool_output_schema: dict[str, Any] | None = None,
        risk_level: str = "low",
    ) -> None:
        self._installation_id = installation_id
        self._app_id = app_id
        self._app_namespace = app_namespace
        self._tool_id = tool_id
        self._tool_name = tool_name
        self._action = action or tool_name
        self._tool_description = tool_description
        self._tool_input_schema = tool_input_schema
        self._tool_output_schema = tool_output_schema or {"type": "object"}
        self._tool_required_scopes = tool_required_scopes
        self._risk_level = risk_level

    @property
    def installation_id(self) -> str:
        return self._installation_id

    @property
    def app_id(self) -> str:
        return self._app_id

    @property
    def app_namespace(self) -> str:
        return self._app_namespace

    @property
    def tool_id(self) -> str:
        return self._tool_id

    @property
    def tool_name(self) -> str:
        return self._tool_name

    @property
    def action(self) -> str:
        return self._action

    @property
    def source(self) -> str:
        return "app"

    @property
    def namespace(self) -> str:
        return f"hasn.{self._app_namespace}"

    @property
    def name(self) -> str:
        """工具名称格式: hasn.{app_namespace}.{action}"""
        return f"hasn.{self._app_namespace}.{self._action}"

    @property
    def description(self) -> str:
        return self._tool_description

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._tool_input_schema

    @property
    def output_schema(self) -> dict[str, Any]:
        return self._tool_output_schema

    @property
    def required_scopes(self) -> list[str]:
        return self._tool_required_scopes

    @property
    def risk_level(self) -> str:
        return self._risk_level

    def to_mcp_tool(self) -> SimpleNamespace:
        """Compatibility helper for legacy test fixtures and projections."""
        return SimpleNamespace(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
            outputSchema=self.output_schema,
            requiredScopes=self.required_scopes,
            riskLevel=self.risk_level,
        )

    async def execute(
        self,
        agent_context: AgentContext,
        arguments: dict[str, Any],
    ) -> Any:
        """执行应用工具，通过 Runtime Gateway 调用。"""
        async with async_db_session() as db:
            return await runtime_gateway.handle_tool_call(
                db=db,
                installation_id=self._installation_id,
                tool_id=self._tool_id,
                input_data=arguments,
                trace_id=None,
            )


async def load_app_tools_for_agent(
    agent_id: str,
    owner_id: str,
) -> list[AppTool]:
    """
    为指定 Agent 加载所有可用的 App Tools
    """
    tools: list[AppTool] = []

    async with async_db_session() as db:
        installations = await _list_target_installations(
            db=db,
            owner_id=str(owner_id),
            agent_id=agent_id,
        )

        for installation in installations:
            app = await app_manifests_dao.get_by_app_id(db, installation.app_id)
            if not app:
                continue

            tool_defs = list(await app_tools_dao.get_by_app_id(db, installation.app_id))
            if not tool_defs:
                tool_defs = await _tool_defs_from_manifest(db, installation.app_id, installation.installed_version)

            tools.extend(_build_app_tools_for_installation(app, installation, tool_defs, agent_id=agent_id))

    logger.info("Loaded %s app tools for agent %s", len(tools), agent_id)
    return tools


async def load_app_tools_for_owner(owner_id: str) -> list[AppTool]:
    """
    为指定 Owner 加载所有可用的 App Tools
    """
    tools: list[AppTool] = []

    async with async_db_session() as db:
        installations = await app_installations_dao.get_by_owner(db, str(owner_id))

        for installation in installations:
            if installation.status != "active":
                continue

            app = await app_manifests_dao.get_by_app_id(db, installation.app_id)
            if not app:
                continue

            tool_defs = list(await app_tools_dao.get_by_app_id(db, installation.app_id))
            if not tool_defs:
                tool_defs = await _tool_defs_from_manifest(db, installation.app_id, installation.installed_version)

            tools.extend(_build_app_tools_for_installation(app, installation, tool_defs))

    logger.info("Loaded %s app tools for owner %s", len(tools), owner_id)
    return tools


async def _list_target_installations(
    db: AsyncSession,
    owner_id: str,
    agent_id: str,
) -> list[Any]:
    owner_installations = await app_installations_dao.get_by_owner(db, owner_id)
    bound_installation_ids = {
        binding.installation_id
        for binding in await app_agent_bindings_dao.get_all(db)
        if binding.agent_id == agent_id and binding.status == "active"
    }

    if not bound_installation_ids:
        return [installation for installation in owner_installations if installation.status == "active"]

    return [
        installation
        for installation in owner_installations
        if installation.status == "active" and installation.installation_id in bound_installation_ids
    ]


async def _tool_defs_from_manifest(
    db: AsyncSession,
    app_id: str,
    installed_version: str,
) -> list[Any]:
    version = await app_versions_dao.get_by_app_and_version(
        db=db,
        app_id=app_id,
        version=installed_version,
    )
    manifest_tools = (
        version.manifest_snapshot.get("tools", [])
        if version and isinstance(version.manifest_snapshot, dict)
        else []
    )
    return [_tool_from_manifest_snapshot(tool_def) for tool_def in manifest_tools]


def _build_app_tool(app: Any, installation: Any, tool_def: Any) -> AppTool:
    tool_name = getattr(tool_def, "tool_name", None) or _tool_name_from_any(tool_def)
    tool_id = getattr(tool_def, "tool_id", None) or tool_name
    action = tool_name
    required_scopes = getattr(tool_def, "required_scopes", None) or []
    if isinstance(required_scopes, dict):
        required_scopes = list(required_scopes.values())

    return AppTool(
        installation_id=installation.installation_id,
        app_id=app.app_id,
        app_namespace=app.namespace or app.app_id,
        tool_id=tool_id,
        tool_name=tool_name,
        action=action,
        tool_description=getattr(tool_def, "description", "") or "",
        tool_input_schema=getattr(tool_def, "input_schema", {}) or {},
        tool_output_schema=getattr(tool_def, "output_schema", {}) or {},
        tool_required_scopes=list(required_scopes),
        risk_level=getattr(tool_def, "risk_level", "") or "low",
    )


def _build_app_tools_for_installation(
    app: Any,
    installation: Any,
    tool_defs: list[Any],
    *,
    agent_id: str | None = None,
) -> list[AppTool]:
    tools: list[AppTool] = []
    for tool_def in tool_defs:
        app_tool = _try_build_app_tool(app, installation, tool_def)
        if not app_tool:
            continue
        tools.append(app_tool)
        if agent_id:
            logger.debug("Loaded app tool: %s for agent %s", app_tool.name, agent_id)
    return tools


def _try_build_app_tool(app: Any, installation: Any, tool_def: Any) -> AppTool | None:
    try:
        return _build_app_tool(app, installation, tool_def)
    except Exception as e:
        logger.error(
            "Failed to load tool %s from installation %s: %s",
            _tool_name_from_any(tool_def),
            installation.installation_id,
            e,
        )
        return None


def _tool_from_manifest_snapshot(tool_def: dict[str, Any]) -> Any:
    return type(
        "AppToolSnapshot",
        (),
        {
            "tool_id": tool_def.get("tool_id") or tool_def.get("name") or tool_def.get("tool_name", ""),
            "tool_name": tool_def.get("tool_name") or tool_def.get("name", ""),
            "description": tool_def.get("description", ""),
            "input_schema": tool_def.get("input_schema", {}),
            "output_schema": tool_def.get("output_schema", {}),
            "risk_level": tool_def.get("risk_level", "low"),
            "required_scopes": tool_def.get("required_scopes", []),
        },
    )()


def _tool_source_namespace(app: Any) -> str:
    return getattr(app, "namespace", "") or getattr(app, "app_id", "")


def _tool_name_from_any(tool_def: Any) -> str:
    if isinstance(tool_def, dict):
        return str(tool_def.get("tool_name") or tool_def.get("name") or "")
    return str(getattr(tool_def, "tool_name", "") or getattr(tool_def, "name", "") or "")
