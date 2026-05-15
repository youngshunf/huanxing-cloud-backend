"""
Runtime Gateway

App 运行时网关，负责 Tool 调用的权限校验、参数验证、执行和审计
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_tools import app_tools_dao
from backend.app.app_platform.service.installation_service import installation_service
from backend.app.app_platform.service.permission_audit_service import permission_audit_service
from backend.app.app_platform.service.permission_validator import permission_validator
from backend.common.exception import errors


class RuntimeGateway:
    """Runtime Gateway - App 运行时网关"""

    @staticmethod
    async def handle_tool_call(
        db: AsyncSession,
        installation_id: str,
        tool_id: str,
        input_data: dict[str, Any],
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        处理 Tool 调用请求

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param tool_id: Tool ID
        :param input_data: 输入数据
        :param trace_id: 追踪 ID
        :return: Tool 执行结果
        """
        # 1. 获取 Installation
        installation = await installation_service.get_installation(db, installation_id)

        # 2. 检查 Installation 状态
        if installation.status != 'active':
            raise errors.ForbiddenError(
                msg=f'Installation 状态不正确: {installation.status}',
                data={'error_code': 'ERR_INSTALLATION_INACTIVE'},
            )

        # 3. 获取 Tool 定义
        tool = await app_tools_dao.get_by_tool_id(db, tool_id)
        if not tool:
            raise errors.NotFoundError(msg=f'Tool {tool_id} 不存在')

        # 4. 检查 Tool 是否属于该 App
        if tool.app_id != installation.app_id:
            raise errors.ForbiddenError(msg='Tool 不属于该 App')

        # 5. 权限校验
        await permission_validator.check_scopes(
            db=db,
            installation_id=installation_id,
            required_scopes=tool.required_scopes or [],
            action_context={
                'action': 'hasn.app.tool.call',
                'tool_id': tool_id,
                'input': input_data,
            },
        )

        # 6. 参数校验（TODO: 根据 input_schema 校验）
        # await RuntimeGateway._validate_input(input_data, tool.input_schema)

        # 7. 执行 Tool（TODO: 实际调用 App Backend）
        result = await RuntimeGateway._execute_tool(
            db=db,
            installation=installation,
            tool=tool,
            input_data=input_data,
        )

        # 8. 审计日志
        await permission_audit_service.log_scope_usage(
            db=db,
            event_type='scope_used',
            installation_id=installation_id,
            scope=tool.required_scopes[0] if tool.required_scopes else 'none',
            decision='allow',
            owner_id=installation.owner_id,
            app_id=installation.app_id,
            action='hasn.app.tool.call',
            resource_type='tool',
            resource_id=tool_id,
            trace_id=trace_id,
        )

        return result

    @staticmethod
    async def _execute_tool(
        db: AsyncSession,
        installation: Any,
        tool: Any,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        执行 Tool

        :param db: 数据库会话
        :param installation: Installation 对象
        :param tool: Tool 对象
        :param input_data: 输入数据
        :return: 执行结果
        """
        # TODO: 根据 backend_runtime_mode 调用不同的执行器
        # - platform_hosted: 直接调用平台托管的 Python 函数
        # - external_hosted: 通过 HTTP 调用外部 Backend

        # 暂时返回模拟结果
        return {
            'success': True,
            'data': {
                'message': f'Tool {tool.tool_name} executed successfully',
                'input': input_data,
            },
        }


runtime_gateway: RuntimeGateway = RuntimeGateway()
