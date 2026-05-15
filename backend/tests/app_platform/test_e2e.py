"""
应用平台端到端测试（简化版）

测试核心流程：
1. 权限授予和验证
2. App Tool 创建和属性验证
3. 多安装场景
"""
import pytest
import uuid

from backend.app.mcp.tools.app_tools import AppTool


def test_app_tool_e2e_creation():
    """
    端到端测试：App Tool 创建和验证

    验证 App Tool 的完整属性和行为
    """
    installation_id = str(uuid.uuid4())

    # 创建 App Tool
    tool = AppTool(
        installation_id=installation_id,
        tool_name="send_notification",
        tool_description="Send a notification to users",
        tool_input_schema={
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Recipient ID"},
                "message": {"type": "string", "description": "Message content"}
            },
            "required": ["recipient", "message"]
        },
        tool_required_scopes=["hasn.im.send"],
    )

    # 验证基本属性
    assert tool.name == f"app.{installation_id}.send_notification"
    assert tool.description == "Send a notification to users"
    assert tool.required_scopes == ["hasn.im.send"]

    # 验证输入 schema
    assert tool.input_schema["type"] == "object"
    assert "recipient" in tool.input_schema["properties"]
    assert "message" in tool.input_schema["properties"]
    assert tool.input_schema["required"] == ["recipient", "message"]

    # 验证转换为 MCP Tool
    mcp_tool = tool.to_mcp_tool()
    assert mcp_tool.name == tool.name
    assert mcp_tool.description == tool.description
    assert mcp_tool.inputSchema == tool.input_schema


def test_app_tool_e2e_multiple_scopes():
    """
    端到端测试：多权限 Tool

    验证需要多个权限的 Tool
    """
    installation_id = str(uuid.uuid4())

    tool = AppTool(
        installation_id=installation_id,
        tool_name="complex_operation",
        tool_description="Complex operation requiring multiple permissions",
        tool_input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string"}
            }
        },
        tool_required_scopes=[
            "hasn.im.send",
            "hasn.data.read",
            "hasn.data.write",
            "hasn.agent.invoke"
        ],
    )

    # 验证所有权限都被记录
    assert len(tool.required_scopes) == 4
    assert "hasn.im.send" in tool.required_scopes
    assert "hasn.data.read" in tool.required_scopes
    assert "hasn.data.write" in tool.required_scopes
    assert "hasn.agent.invoke" in tool.required_scopes

    # 验证 MCP Tool 转换
    mcp_tool = tool.to_mcp_tool()
    assert mcp_tool.name == f"app.{installation_id}.complex_operation"


def test_app_tool_e2e_multi_installation():
    """
    端到端测试：多安装场景

    验证同一个应用的多个安装产生不同的 Tool 实例
    """
    # 模拟同一个应用安装到两个不同的 Agent
    installation_id_1 = str(uuid.uuid4())
    installation_id_2 = str(uuid.uuid4())

    # 第一个安装的 Tool
    tool_1 = AppTool(
        installation_id=installation_id_1,
        tool_name="shared_tool",
        tool_description="Shared tool",
        tool_input_schema={},
        tool_required_scopes=["hasn.im.send"],
    )

    # 第二个安装的 Tool（相同的 tool_name，但不同的 installation_id）
    tool_2 = AppTool(
        installation_id=installation_id_2,
        tool_name="shared_tool",
        tool_description="Shared tool",
        tool_input_schema={},
        tool_required_scopes=["hasn.im.send"],
    )

    # 验证两个 Tool 的名称不同（因为 installation_id 不同）
    assert tool_1.name != tool_2.name
    assert tool_1.name == f"app.{installation_id_1}.shared_tool"
    assert tool_2.name == f"app.{installation_id_2}.shared_tool"

    # 验证其他属性相同
    assert tool_1.description == tool_2.description
    assert tool_1.required_scopes == tool_2.required_scopes


def test_app_tool_e2e_permission_validation():
    """
    端到端测试：权限验证逻辑

    模拟 MCP Server 的权限检查流程
    """
    installation_id = str(uuid.uuid4())

    # 创建需要特定权限的 Tool
    read_tool = AppTool(
        installation_id=installation_id,
        tool_name="read_data",
        tool_description="Read data",
        tool_input_schema={},
        tool_required_scopes=["hasn.data.read"],
    )

    write_tool = AppTool(
        installation_id=installation_id,
        tool_name="write_data",
        tool_description="Write data",
        tool_input_schema={},
        tool_required_scopes=["hasn.data.write"],
    )

    # 模拟 Agent 拥有的权限
    agent_scopes = ["hasn.data.read", "hasn.im.send"]

    # 验证权限检查逻辑（模拟 MCP Server 的 _check_tool_permission）
    can_use_read = all(scope in agent_scopes for scope in read_tool.required_scopes)
    can_use_write = all(scope in agent_scopes for scope in write_tool.required_scopes)

    # read_tool 应该可用（Agent 有 hasn.data.read）
    assert can_use_read is True

    # write_tool 应该不可用（Agent 没有 hasn.data.write）
    assert can_use_write is False


def test_app_tool_e2e_naming_convention():
    """
    端到端测试：Tool 命名规范

    验证 Tool 命名符合规范：app.{installation_id}.{tool_name}
    """
    test_cases = [
        ("inst_123", "send_message", "app.inst_123.send_message"),
        ("abc-def-456", "query_data", "app.abc-def-456.query_data"),
        ("550e8400-e29b-41d4-a716-446655440000", "hello", "app.550e8400-e29b-41d4-a716-446655440000.hello"),
    ]

    for installation_id, tool_name, expected_name in test_cases:
        tool = AppTool(
            installation_id=installation_id,
            tool_name=tool_name,
            tool_description="Test tool",
            tool_input_schema={},
            tool_required_scopes=[],
        )

        assert tool.name == expected_name


def test_app_tool_e2e_mcp_integration():
    """
    端到端测试：MCP 集成

    验证 App Tool 可以正确转换为 MCP Tool 格式
    """
    installation_id = str(uuid.uuid4())

    tool = AppTool(
        installation_id=installation_id,
        tool_name="test_tool",
        tool_description="A test tool for MCP integration",
        tool_input_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "First parameter"},
                "param2": {"type": "number", "description": "Second parameter"},
                "param3": {"type": "boolean", "description": "Third parameter"}
            },
            "required": ["param1"]
        },
        tool_required_scopes=["hasn.test.execute"],
    )

    # 转换为 MCP Tool
    mcp_tool = tool.to_mcp_tool()

    # 验证 MCP Tool 的所有字段
    assert mcp_tool.name == f"app.{installation_id}.test_tool"
    assert mcp_tool.description == "A test tool for MCP integration"

    # 验证 inputSchema 完整性
    assert mcp_tool.inputSchema["type"] == "object"
    assert len(mcp_tool.inputSchema["properties"]) == 3
    assert "param1" in mcp_tool.inputSchema["properties"]
    assert "param2" in mcp_tool.inputSchema["properties"]
    assert "param3" in mcp_tool.inputSchema["properties"]
    assert mcp_tool.inputSchema["required"] == ["param1"]

    # 验证参数类型
    assert mcp_tool.inputSchema["properties"]["param1"]["type"] == "string"
    assert mcp_tool.inputSchema["properties"]["param2"]["type"] == "number"
    assert mcp_tool.inputSchema["properties"]["param3"]["type"] == "boolean"
