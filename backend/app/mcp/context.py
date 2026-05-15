"""
AgentContext 上下文传递

使用 contextvars 在异步上下文中传递 AgentContext
"""
from contextvars import ContextVar
from typing import Optional

from backend.app.mcp.auth import AgentContext

# 使用 contextvars 在异步上下文中传递 AgentContext
_agent_context_var: ContextVar[Optional[AgentContext]] = ContextVar(
    'agent_context',
    default=None
)


def set_current_agent_context(context: AgentContext) -> None:
    """设置当前 Agent 上下文"""
    _agent_context_var.set(context)


def get_current_agent_context() -> AgentContext:
    """获取当前 Agent 上下文"""
    context = _agent_context_var.get()
    if context is None:
        raise RuntimeError("Agent context not found in current async context")
    return context


def clear_agent_context() -> None:
    """清除当前 Agent 上下文"""
    _agent_context_var.set(None)
