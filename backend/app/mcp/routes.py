"""
MCP 路由

提供 SSE 和 HTTP 端点
"""
import logging
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from backend.app.mcp.auth import AgentContextDep
from backend.app.mcp.context import set_current_agent_context, clear_agent_context
from backend.app.mcp.server import mcp_server

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/sse")
async def mcp_sse_endpoint(
    request: Request,
    agent_context: AgentContextDep
):
    """
    MCP SSE 端点

    Agent Runtime 通过此端点建立 SSE 连接
    """
    logger.info(f"Agent {agent_context.hasn_id} connecting to MCP SSE")

    # 设置 Agent 上下文到 contextvars
    set_current_agent_context(agent_context)

    try:
        # TODO: 实现 SSE 流
        # 这里需要根据实际的 Python MCP SDK API 调整
        # 以下是占位实现
        async def event_generator():
            # 发送初始化消息
            yield {
                "event": "connected",
                "data": f"Agent {agent_context.hasn_id} connected"
            }

            # 等待客户端断开
            while True:
                if await request.is_disconnected():
                    break
                # 这里应该处理 MCP 协议消息
                # await asyncio.sleep(1)

        return EventSourceResponse(event_generator())

    except Exception as e:
        logger.error(f"SSE connection error: {str(e)}", exc_info=True)
        raise
    finally:
        # 清理上下文
        clear_agent_context()
        logger.info(f"Agent {agent_context.hasn_id} disconnected from MCP SSE")


@router.post("/message")
async def mcp_message_endpoint(
    request: Request,
    agent_context: AgentContextDep
):
    """
    MCP 消息端点（HTTP POST）

    备用方案：如果 SSE 不可用，可以使用 HTTP POST
    """
    set_current_agent_context(agent_context)

    try:
        body = await request.json()
        logger.info(f"Agent {agent_context.hasn_id} sent MCP message: {body.get('method')}")

        # TODO: 处理 MCP 消息
        # response = await mcp_server.handle_message(body)
        response = {"error": "Not implemented yet"}

        return response
    except Exception as e:
        logger.error(f"Message handling error: {str(e)}", exc_info=True)
        raise
    finally:
        clear_agent_context()


def register_mcp_routes(app):
    """将 MCP 路由注册到主应用"""
    app.include_router(router)
    logger.info("MCP routes registered")
