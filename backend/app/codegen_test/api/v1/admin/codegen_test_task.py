from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.codegen_test.schema.codegen_test_task import (
    CreateCodegenTestTaskParam,
    DeleteCodegenTestTaskParam,
    GetCodegenTestTaskDetail,
    UpdateCodegenTestTaskParam,
)
from backend.app.codegen_test.service.codegen_test_task_service import codegen_test_task_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取测试任务详情', dependencies=[DependsJwtAuth])
async def get_codegen_test_task(
    db: CurrentSession, pk: Annotated[int, Path(description='测试任务 ID')]
) -> ResponseSchemaModel[GetCodegenTestTaskDetail]:
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    return response_base.success(data=codegen_test_task)


@router.get(
    '',
    summary='分页获取所有测试任务',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_codegen_test_tasks_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetCodegenTestTaskDetail]]:
    page_data = await codegen_test_task_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建测试任务',
    dependencies=[
        Depends(RequestPermission('codegen:test:task:add')),
        DependsRBAC,
    ],
)
async def create_codegen_test_task(db: CurrentSessionTransaction, obj: CreateCodegenTestTaskParam) -> ResponseModel:
    await codegen_test_task_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新测试任务',
    dependencies=[
        Depends(RequestPermission('codegen:test:task:edit')),
        DependsRBAC,
    ],
)
async def update_codegen_test_task(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='测试任务 ID')], obj: UpdateCodegenTestTaskParam
) -> ResponseModel:
    count = await codegen_test_task_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除测试任务',
    dependencies=[
        Depends(RequestPermission('codegen:test:task:del')),
        DependsRBAC,
    ],
)
async def delete_codegen_test_tasks(db: CurrentSessionTransaction, obj: DeleteCodegenTestTaskParam) -> ResponseModel:
    count = await codegen_test_task_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
