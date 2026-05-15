# App Tool 动态注册功能

## 概述

实现了应用平台 Tool 的动态注册功能，允许 MCP Server 根据 Agent 的安装情况，自动加载和注册可用的 App Tools。

## 核心功能

### 1. AppTool 类

动态工具类，封装应用平台的 Tool：

```python
class AppTool(BaseTool):
    """应用平台动态工具"""
    
    @property
    def name(self) -> str:
        """工具名称格式: app.{installation_id}.{tool_name}"""
        return f"app.{self._installation_id}.{self._tool_name}"
```

### 2. 动态加载函数

- `load_app_tools_for_agent()`: 加载 Agent 级别的 App Tools
- `load_app_tools_for_owner()`: 加载 Owner 级别的 App Tools

### 3. MCP Server 集成

在 `list_tools()` 时自动加载 App Tools：

```python
@self.server.list_tools()
async def list_tools() -> list[Tool]:
    # 动态加载 App Tools
    await self._load_app_tools(agent_context)
    
    # 返回所有可用工具（内置 + App）
    return available_tools
```

## 工作流程

```text
1. Agent 请求工具列表
   ↓
2. MCP Server 获取 Agent Context
   ↓
3. 查询该 Agent 的所有 active 安装
   ↓
4. 从每个安装的 manifest 提取 tools
   ↓
5. 创建 AppTool 实例并注册到 ToolRegistry
   ↓
6. 返回工具列表（内置工具 + App Tools）
```

## 工具命名规范

App Tools 使用三段式命名：

```
app.{installation_id}.{tool_name}
```

示例：
- `app.inst_123.send_message`
- `app.inst_456.query_data`

## 权限验证

App Tools 继承应用 manifest 中定义的 `required_scopes`：

```json
{
  "name": "send_message",
  "required_scopes": ["hasn.im.send"]
}
```

调用时会验证：
1. Installation 是否授予了该 scope
2. Agent 是否拥有该 scope

## 测试

新增测试文件：`tests/app_platform/test_app_tools.py`

测试覆盖：
- AppTool 名称格式
- 输入 schema 处理
- 动态加载 Agent Tools
- 动态加载 Owner Tools
- 错误处理（跳过无效工具）

## 使用示例

### 1. 安装应用

```bash
hasn app install \
  --app-id app_123 \
  --owner owner_456 \
  --target-type agent \
  --target-id agent_789 \
  --scopes hasn.im.send
```

### 2. Agent 列出工具

```python
# MCP Client 调用
tools = await mcp_client.list_tools()

# 返回结果包含：
# - 内置工具: hasn.message.send, hasn.contact.list
# - App Tools: app.inst_xxx.send_message
```

### 3. 调用 App Tool

```python
result = await mcp_client.call_tool(
    name="app.inst_xxx.send_message",
    arguments={"recipient": "user123", "message": "Hello"}
)
```

## 文件清单

- `backend/app/mcp/tools/app_tools.py` - App Tool 实现
- `backend/app/mcp/server.py` - MCP Server 集成
- `backend/tests/app_platform/test_app_tools.py` - 单元测试

## 下一步

- [ ] 实现 App Tool 调用的审计日志
- [ ] 添加 App Tool 调用的限流
- [ ] 支持 App Tool 的热重载
- [ ] 实现 App Tool 的性能监控
