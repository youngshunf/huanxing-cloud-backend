"""测试任务 - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.codegen_test.schema.codegen_test_task import (
    CreateCodegenTestTaskParam,
    UpdateCodegenTestTaskParam,
)
from backend.app.codegen_test.service.codegen_test_task_service import codegen_test_task_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='测试任务列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_codegen_test_tasks(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await codegen_test_task_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建测试任务',
    dependencies=[DependsAgentAuth],
)
async def agent_create_codegen_test_task(
    db: CurrentSessionTransaction,
    obj: CreateCodegenTestTaskParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await codegen_test_task_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取测试任务详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_codegen_test_task(
    db: CurrentSession,
    pk: Annotated[int, Path(description='测试任务 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    if codegen_test_task.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该测试任务')
    return response_base.success(data=codegen_test_task)


@router.put(
    '/{pk}',
    summary='更新测试任务',
    dependencies=[DependsAgentAuth],
)
async def agent_update_codegen_test_task(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='测试任务 ID')],
    obj: UpdateCodegenTestTaskParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    if codegen_test_task.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该测试任务')
    count = await codegen_test_task_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除测试任务',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_codegen_test_task(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='测试任务 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    if codegen_test_task.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该测试任务')
    from backend.app.codegen_test.schema.codegen_test_task import DeleteCodegenTestTaskParam
    count = await codegen_test_task_service.delete(db=db, obj=DeleteCodegenTestTaskParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
