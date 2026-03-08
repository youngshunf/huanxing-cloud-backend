from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_project import (
    CreateHxCreatorProjectParam,
    DeleteHxCreatorProjectParam,
    GetHxCreatorProjectDetail,
    UpdateHxCreatorProjectParam,
)
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取创作项目详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_project(
    db: CurrentSession, pk: Annotated[int, Path(description='创作项目 ID')]
) -> ResponseSchemaModel[GetHxCreatorProjectDetail]:
    hx_creator_project = await hx_creator_project_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_project)


@router.get(
    '',
    summary='分页获取所有创作项目',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_projects_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorProjectDetail]]:
    page_data = await hx_creator_project_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建创作项目',
    dependencies=[
        Depends(RequestPermission('hx:creator:project:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_project(db: CurrentSessionTransaction, obj: CreateHxCreatorProjectParam) -> ResponseModel:
    await hx_creator_project_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新创作项目',
    dependencies=[
        Depends(RequestPermission('hx:creator:project:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_project(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='创作项目 ID')], obj: UpdateHxCreatorProjectParam
) -> ResponseModel:
    count = await hx_creator_project_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除创作项目',
    dependencies=[
        Depends(RequestPermission('hx:creator:project:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_projects(db: CurrentSessionTransaction, obj: DeleteHxCreatorProjectParam) -> ResponseModel:
    count = await hx_creator_project_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
