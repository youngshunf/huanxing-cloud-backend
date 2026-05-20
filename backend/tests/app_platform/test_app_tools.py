"""App Tool 动态注册测试."""

from backend.app.mcp.tools.app_tools import AppTool


def make_app_tool(
    *,
    installation_id: str = "appi_test",
    app_namespace: str = "knowledge",
    tool_id: str = "knowledge.search",
    tool_name: str = "search",
    tool_description: str = "Search knowledge",
    tool_input_schema: dict | None = None,
    tool_required_scopes: list[str] | None = None,
) -> AppTool:
    return AppTool(
        installation_id=installation_id,
        app_id=app_namespace,
        app_namespace=app_namespace,
        tool_id=tool_id,
        tool_name=tool_name,
        action=tool_name,
        tool_description=tool_description,
        tool_input_schema=tool_input_schema or {},
        tool_required_scopes=tool_required_scopes or [],
    )


def test_app_tool_name_format() -> None:
    """测试 App Tool 名称格式"""
    tool = make_app_tool(
        installation_id="inst123",
        app_namespace="community",
        tool_id="create_post",
        tool_name="create_post",
        tool_description="Send a message",
        tool_required_scopes=["hasn.im.send"],
    )

    assert tool.name == "hasn.community.create_post"
    assert "inst123" not in tool.name
    assert tool.description == "Send a message"
    assert tool.required_scopes == ["hasn.im.send"]


def test_app_tool_input_schema() -> None:
    """测试 App Tool 输入 schema"""
    schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        },
        "required": ["message"]
    }

    tool = make_app_tool(
        tool_name="hello",
        tool_description="Say hello",
        tool_input_schema=schema,
    )

    assert tool.input_schema == schema


def test_app_tool_to_mcp_tool() -> None:
    """测试转换为 MCP Tool"""
    tool = make_app_tool(
        installation_id="inst456",
        app_namespace="data",
        tool_id="query_data",
        tool_name="query_data",
        tool_description="Query data from database",
        tool_input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            }
        },
        tool_required_scopes=["hasn.data.read"],
    )

    mcp_tool = tool.to_mcp_tool()

    assert mcp_tool.name == "hasn.data.query_data"
    assert mcp_tool.description == "Query data from database"
    assert mcp_tool.inputSchema["type"] == "object"


def test_app_tool_multiple_scopes() -> None:
    """测试多个权限 scope"""
    tool = make_app_tool(
        app_namespace="operations",
        tool_id="complex_action",
        tool_name="complex_action",
        tool_description="Complex action requiring multiple scopes",
        tool_required_scopes=["hasn.im.send", "hasn.data.write", "hasn.agent.invoke"],
    )

    assert len(tool.required_scopes) == 3
    assert "hasn.im.send" in tool.required_scopes
    assert "hasn.data.write" in tool.required_scopes
    assert "hasn.agent.invoke" in tool.required_scopes
