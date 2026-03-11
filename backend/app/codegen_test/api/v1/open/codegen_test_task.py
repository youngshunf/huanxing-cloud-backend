"""测试任务 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.codegen_test.schema.codegen_test_task import GetCodegenTestTaskDetail
from backend.app.codegen_test.service.codegen_test_task_service import codegen_test_task_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取测试任务列表',
    dependencies=[DependsPagination],
)
async def get_codegen_test_tasks(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetCodegenTestTaskDetail]]:
    page_data = await codegen_test_task_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取测试任务详情',
)
async def get_codegen_test_task(
    db: CurrentSession,
    pk: Annotated[int, Path(description='测试任务 ID')],
) -> ResponseSchemaModel[GetCodegenTestTaskDetail]:
    codegen_test_task = await codegen_test_task_service.get(db=db, pk=pk)
    return response_base.success(data=codegen_test_task)
