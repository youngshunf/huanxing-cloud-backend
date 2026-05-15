"""
App Tool 动态注册测试
"""
import pytest

from backend.app.mcp.tools.app_tools import AppTool


def test_app_tool_name_format():
    """测试 App Tool 名称格式"""
    tool = AppTool(
        installation_id="inst123",
        tool_name="send_message",
        tool_description="Send a message",
        tool_input_schema={},
        tool_required_scopes=["hasn.im.send"],
    )

    assert tool.name == "app.inst123.send_message"
    assert tool.description == "Send a message"
    assert tool.required_scopes == ["hasn.im.send"]


def test_app_tool_input_schema():
    """测试 App Tool 输入 schema"""
    schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        },
        "required": ["message"]
    }

    tool = AppTool(
        installation_id="inst123",
        tool_name="hello",
        tool_description="Say hello",
        tool_input_schema=schema,
        tool_required_scopes=[],
    )

    assert tool.input_schema == schema


def test_app_tool_to_mcp_tool():
    """测试转换为 MCP Tool"""
    tool = AppTool(
        installation_id="inst456",
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

    assert mcp_tool.name == "app.inst456.query_data"
    assert mcp_tool.description == "Query data from database"
    assert mcp_tool.inputSchema["type"] == "object"


def test_app_tool_multiple_scopes():
    """测试多个权限 scope"""
    tool = AppTool(
        installation_id="inst789",
        tool_name="complex_action",
        tool_description="Complex action requiring multiple scopes",
        tool_input_schema={},
        tool_required_scopes=["hasn.im.send", "hasn.data.write", "hasn.agent.invoke"],
    )

    assert len(tool.required_scopes) == 3
    assert "hasn.im.send" in tool.required_scopes
    assert "hasn.data.write" in tool.required_scopes
    assert "hasn.agent.invoke" in tool.required_scopes
