"""new-api 用量查询与额度 — 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 自动关联 new-api 映射
"""

import time
from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.llm.schema.llm_newapi_user_mapping import (
    NewApiMappingInfo,
    NewApiQuotaInfo,
    NewApiUsageDetail,
    NewApiUsageSummary,
)
from backend.app.llm.service.llm_newapi_user_mapping_service import llm_newapi_user_mapping_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '/quota',
    summary='查询用户 LLM 剩余额度',
    dependencies=[DependsJwtAuth],
)
async def get_newapi_quota(request: Request, db: CurrentSession) -> ResponseSchemaModel[NewApiQuotaInfo]:
    data = await llm_newapi_user_mapping_service.get_quota_info(db, request.user.id)
    return response_base.success(data=data)


@router.get(
    '/usage/summary',
    summary='查询用量统计概览（按模型分组）',
    dependencies=[DependsJwtAuth],
)
async def get_newapi_usage_summary(
    request: Request,
    db: CurrentSession,
    start_time: Annotated[int | None, Query(description='开始时间 (unix timestamp)')] = None,
    end_time: Annotated[int | None, Query(description='结束时间 (unix timestamp)')] = None,
) -> ResponseSchemaModel[NewApiUsageSummary]:
    now = int(time.time())
    if not start_time:
        start_time = now - 30 * 86400
    if not end_time:
        end_time = now
    data = await llm_newapi_user_mapping_service.get_usage_summary(
        db, request.user.id, start_time, end_time,
    )
    return response_base.success(data=data)


@router.get(
    '/usage/detail',
    summary='查询用量明细（分页）',
    dependencies=[DependsJwtAuth],
)
async def get_newapi_usage_detail(
    request: Request,
    db: CurrentSession,
    start_time: Annotated[int | None, Query(description='开始时间 (unix timestamp)')] = None,
    end_time: Annotated[int | None, Query(description='结束时间 (unix timestamp)')] = None,
    model_name: Annotated[str | None, Query(description='模型名称筛选')] = None,
    limit: Annotated[int, Query(ge=1, le=200, description='每页条数')] = 50,
    offset: Annotated[int, Query(ge=0, description='偏移量')] = 0,
) -> ResponseSchemaModel[NewApiUsageDetail]:
    now = int(time.time())
    if not start_time:
        start_time = now - 30 * 86400
    if not end_time:
        end_time = now
    data = await llm_newapi_user_mapping_service.get_usage_detail(
        db, request.user.id, start_time, end_time,
        model_name=model_name, limit=limit, offset=offset,
    )
    return response_base.success(data=data)


@router.get(
    '/api-key',
    summary='获取用户的 new-api API Key',
    dependencies=[DependsJwtAuth],
)
async def get_newapi_key(request: Request, db: CurrentSession) -> ResponseSchemaModel:
    key = await llm_newapi_user_mapping_service.get_api_key(db, request.user.id)
    return response_base.success(data={'api_key': key})


@router.get(
    '/mapping',
    summary='获取/创建用户的 new-api 映射',
    dependencies=[DependsJwtAuth],
)
async def get_mapping_info(request: Request, db: CurrentSession) -> ResponseSchemaModel[NewApiMappingInfo]:
    nickname = getattr(request.user, 'nickname', '') or ''
    data = await llm_newapi_user_mapping_service.ensure_newapi_user(
        db, request.user.id, nickname=nickname,
    )
    return response_base.success(data=data)
