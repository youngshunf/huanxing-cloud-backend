"""AI lead automation collection job - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.lead_automation.schema.lead_collection_job import GetLeadCollectionJobDetail
from backend.app.lead_automation.service.lead_collection_job_service import lead_collection_job_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取AI lead automation collection job列表',
    dependencies=[DependsPagination],
)
async def get_lead_collection_jobs(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetLeadCollectionJobDetail]]:
    page_data = await lead_collection_job_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取AI lead automation collection job详情',
)
async def get_lead_collection_job(
    db: CurrentSession,
    pk: Annotated[int, Path(description='AI lead automation collection job ID')],
) -> ResponseSchemaModel[GetLeadCollectionJobDetail]:
    lead_collection_job = await lead_collection_job_service.get(db=db, pk=pk)
    return response_base.success(data=lead_collection_job)
