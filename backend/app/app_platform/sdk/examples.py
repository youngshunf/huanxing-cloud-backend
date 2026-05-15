#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App SDK 使用示例

演示如何在应用中使用 SDK
"""
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.sdk.app_sdk import AppSDK


async def example_tool_handler(
    owner_id: str,
    app_id: str,
    installation_id: str,
    tool_name: str,
    parameters: dict,
    db: AsyncSession,
) -> dict:
    """
    示例：Tool 调用处理器

    演示如何在 Tool 中使用 SDK
    """
    # 1. 创建 SDK 实例
    sdk = AppSDK.create(
        owner_id=owner_id,
        app_id=app_id,
        installation_id=installation_id,
        db=db,
    )

    # 2. 检查权限
    required_scope = f"hasn.app.tool.{tool_name}"
    if not await sdk.permission.has_permission(required_scope):
        await sdk.audit.log_tool_call(
            tool_id=tool_name,
            tool_name=tool_name,
            parameters=parameters,
            result='denied',
            error='Permission denied',
        )
        raise PermissionError(f"Missing permission: {required_scope}")

    # 3. 执行业务逻辑
    try:
        # 读取数据
        data = await sdk.data.get(
            resource_id='user_preferences',
            record_key=owner_id,
        )

        # 处理逻辑
        result = {
            'status': 'success',
            'data': data,
            'message': f'Tool {tool_name} executed successfully',
        }

        # 写入数据
        await sdk.data.set(
            resource_id='execution_history',
            record_key=f"{owner_id}:{tool_name}",
            data={
                'tool_name': tool_name,
                'parameters': parameters,
                'result': result,
            },
        )

        # 记录审计日志
        await sdk.audit.log_tool_call(
            tool_id=tool_name,
            tool_name=tool_name,
            parameters=parameters,
            result='success',
        )

        return result

    except Exception as e:
        # 记录失败日志
        await sdk.audit.log_tool_call(
            tool_id=tool_name,
            tool_name=tool_name,
            parameters=parameters,
            result='failure',
            error=str(e),
        )
        raise


async def example_data_operations(
    owner_id: str,
    app_id: str,
    installation_id: str,
    db: AsyncSession,
):
    """
    示例：数据操作

    演示如何使用数据客户端
    """
    sdk = AppSDK.create(
        owner_id=owner_id,
        app_id=app_id,
        installation_id=installation_id,
        db=db,
    )

    # 写入数据
    await sdk.data.set(
        resource_id='todos',
        record_key='todo-1',
        data={
            'title': 'Buy milk',
            'completed': False,
            'created_at': '2026-05-14T10:00:00Z',
        },
    )

    # 读取数据
    todo = await sdk.data.get(
        resource_id='todos',
        record_key='todo-1',
    )

    # 列出数据
    todos = await sdk.data.list(
        resource_id='todos',
        prefix='todo-',
        limit=10,
    )

    # 查询数据
    completed_todos = await sdk.data.query(
        resource_id='todos',
        filter_json={'completed': True},
        limit=10,
    )

    # 删除数据
    await sdk.data.delete(
        resource_id='todos',
        record_key='todo-1',
    )

    # 记录审计日志
    await sdk.audit.log_data_access(
        operation='read',
        resource_id='todos',
        record_key='todo-1',
        result='success',
    )


async def example_permission_operations(
    owner_id: str,
    app_id: str,
    installation_id: str,
    db: AsyncSession,
):
    """
    示例：权限操作

    演示如何使用权限客户端
    """
    sdk = AppSDK.create(
        owner_id=owner_id,
        app_id=app_id,
        installation_id=installation_id,
        db=db,
    )

    # 检查权限
    has_perm = await sdk.permission.has_permission('hasn.app.data.write')

    # 获取已授予的权限列表
    granted_scopes = await sdk.permission.get_granted_scopes()

    # 请求动态权限
    request_id = await sdk.permission.request_permission(
        scope='hasn.app.agent.invoke',
        reason='Need to call agent for complex task',
    )

    # 检查请求状态
    status = await sdk.permission.check_permission_status(request_id)
