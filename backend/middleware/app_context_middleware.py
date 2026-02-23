"""应用上下文中间件 - 解析 X-App-Code 请求头，注入应用标识
@author Ysf
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# 有效的应用标识
VALID_APP_CODES = {'huanxing', 'zhixiaoya'}

# 默认应用标识
DEFAULT_APP_CODE = 'huanxing'


class AppContextMiddleware(BaseHTTPMiddleware):
    """应用上下文中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        解析 X-App-Code 请求头，注入到 request.state.app_code

        :param request: FastAPI 请求对象
        :param call_next: 下一个中间件或路由处理函数
        :return:
        """
        app_code = request.headers.get('X-App-Code', DEFAULT_APP_CODE)
        if app_code not in VALID_APP_CODES:
            app_code = DEFAULT_APP_CODE
        request.state.app_code = app_code

        response = await call_next(request)
        return response
