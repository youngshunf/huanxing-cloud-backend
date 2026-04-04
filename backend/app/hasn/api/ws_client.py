"""HASN 旧版客户端 WebSocket 端点（兼容重定向）

此文件仅保留旧 /ws/client 端点的路由，所有逻辑已迁移到 ws_node.py。
新代码请使用 /ws/node 端点。
"""

# ws_node.py 中的 /ws/client 兼容路由已处理所有旧客户端连接。
# 如果此文件被独立挂载为路由，则重新导出 ws_node 的路由。

from backend.app.hasn.api.ws_node import router  # noqa: F401
