"""
应用平台端到端测试（简化版）

测试核心流程：
1. 权限授予和验证
2. App Tool 创建和属性验证
3. 多安装场景
"""
import uuid

from backend.app.mcp.tools.app_tools import AppTool


def make_app_tool(
    *,
    installation_id: str | None = None,
    app_namespace: str = "community",
    tool_id: str = "create_post",
    tool_name: str = "create_post",
    tool_description: str = "App tool",
    tool_input_schema: dict | None = None,
    tool_required_scopes: list[str] | None = None,
) -> AppTool:
    return AppTool(
        installation_id=installation_id or str(uuid.uuid4()),
        app_id=app_namespace,
        app_namespace=app_namespace,
        tool_id=tool_id,
        tool_name=tool_name,
        action=tool_name,
        tool_description=tool_description,
        tool_input_schema=tool_input_schema or {},
        tool_required_scopes=tool_required_scopes or [],
    )


def test_app_tool_e2e_creation() -> None:
    """
    端到端测试：App Tool 创建和验证

    验证 App Tool 的完整属性和行为
    """
    # 创建 App Tool
    tool = make_app_tool(
        app_namespace="notification",
        tool_id="send_notification",
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
    assert tool.name == "hasn.notification.send_notification"
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


def test_app_tool_e2e_multiple_scopes() -> None:
    """
    端到端测试：多权限 Tool

    验证需要多个权限的 Tool
    """
    tool = make_app_tool(
        app_namespace="operations",
        tool_id="complex_operation",
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
    assert mcp_tool.name == "hasn.operations.complex_operation"


def test_app_tool_e2e_multi_installation() -> None:
    """
    端到端测试：多安装场景

    验证同一个应用的多个安装产生不同的 Tool 实例
    """
    # 模拟同一个应用安装到两个不同的 Agent
    installation_id_1 = str(uuid.uuid4())
    installation_id_2 = str(uuid.uuid4())

    # 第一个安装的 Tool
    tool_1 = make_app_tool(
        installation_id=installation_id_1,
        app_namespace="shared",
        tool_id="shared_tool",
        tool_name="shared_tool",
        tool_description="Shared tool",
        tool_required_scopes=["hasn.im.send"],
    )

    # 第二个安装的 Tool（相同的 tool_name，但不同的 installation_id）
    tool_2 = make_app_tool(
        installation_id=installation_id_2,
        app_namespace="shared",
        tool_id="shared_tool",
        tool_name="shared_tool",
        tool_description="Shared tool",
        tool_required_scopes=["hasn.im.send"],
    )

    # canonical name 不编码 installation，运行时上下文由 Gateway 决定
    assert tool_1.name == tool_2.name
    assert tool_1.name == "hasn.shared.shared_tool"

    # 验证其他属性相同
    assert tool_1.description == tool_2.description
    assert tool_1.required_scopes == tool_2.required_scopes


def test_app_tool_e2e_permission_validation() -> None:
    """
    端到端测试：权限验证逻辑

    模拟 MCP Server 的权限检查流程
    """
    # 创建需要特定权限的 Tool
    read_tool = make_app_tool(
        app_namespace="data",
        tool_id="read_data",
        tool_name="read_data",
        tool_description="Read data",
        tool_required_scopes=["hasn.data.read"],
    )

    write_tool = make_app_tool(
        app_namespace="data",
        tool_id="write_data",
        tool_name="write_data",
        tool_description="Write data",
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


def test_app_tool_e2e_naming_convention() -> None:
    """
    端到端测试：Tool 命名规范

    验证 Tool 命名符合规范：hasn.{app_namespace}.{action}
    """
    test_cases = [
        ("inst_123", "community", "send_message", "hasn.community.send_message"),
        ("abc-def-456", "data", "query_data", "hasn.data.query_data"),
        ("550e8400-e29b-41d4-a716-446655440000", "hello", "world", "hasn.hello.world"),
    ]

    for installation_id, app_namespace, tool_name, expected_name in test_cases:
        tool = make_app_tool(
            installation_id=installation_id,
            app_namespace=app_namespace,
            tool_id=tool_name,
            tool_name=tool_name,
            tool_description="Test tool",
        )

        assert tool.name == expected_name


def test_app_tool_e2e_mcp_integration() -> None:
    """
    端到端测试：MCP 集成

    验证 App Tool 可以正确转换为 MCP Tool 格式
    """
    tool = make_app_tool(
        app_namespace="test",
        tool_id="test_tool",
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
    assert mcp_tool.name == "hasn.test.test_tool"
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
