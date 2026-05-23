"""Skill Bundle 定义表（多个 skill 的组合） - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_skill_bundle import GetHasnSkillBundleDetail
from backend.app.hasn.service.hasn_skill_bundle_service import hasn_skill_bundle_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取Skill Bundle 定义表（多个 skill 的组合）列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_skill_bundle',
)
async def get_hasn_skill_bundle(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnSkillBundleDetail]]:
    page_data = await hasn_skill_bundle_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取Skill Bundle 定义表（多个 skill 的组合）详情',
    name='open_get_hasn_skill_bundle_detail',
)
async def get_hasn_skill_bundle_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Skill Bundle 定义表（多个 skill 的组合） ID')],
) -> ResponseSchemaModel[GetHasnSkillBundleDetail]:
    hasn_skill_bundle = await hasn_skill_bundle_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_skill_bundle)
