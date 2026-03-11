"""测试任务 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.codegen_test.schema.codegen_test_task import (
    CreateCodegenTestTaskParam,
    GetCodegenTestTaskDetail,
    UpdateCodegenTestTaskParam,
)
from backend.app.codegen_test.service.codegen_test_task_service import codegen_test_task_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的测试任务列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_codegen_test_tasks(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetCodegenTestTaskDetail]]:
    user_id = request.user.id
    page_data = await codegen_test_task_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建测试任务',
    dependencies=[DependsJwtAuth],
)
async def create_my_codegen_test_task(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateCodegenTestTaskParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await codegen_test_task_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取测试任务详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_codegen_test_task(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='测试任务 ID')],
) -> ResponseSchemaModel[GetCodegenTestTaskDetail]:
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    if codegen_test_task.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该测试任务')
    return response_base.success(data=codegen_test_task)


@router.put(
    '/{pk}',
    summary='更新测试任务',
    dependencies=[DependsJwtAuth],
)
async def update_my_codegen_test_task(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='测试任务 ID')],
    obj: UpdateCodegenTestTaskParam,
) -> ResponseModel:
    user_id = request.user.id
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
    dependencies=[DependsJwtAuth],
)
async def delete_my_codegen_test_task(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='测试任务 ID')],
) -> ResponseModel:
    user_id = request.user.id
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    if codegen_test_task.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该测试任务')
    from backend.app.codegen_test.schema.codegen_test_task import DeleteCodegenTestTaskParam
    count = await codegen_test_task_service.delete(db=db, obj=DeleteCodegenTestTaskParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
