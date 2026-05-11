"""HASN 用户端合并 profile API.

`GET/PUT /api/v1/hasn/app/profile/me` — 合并 sys_user + hasn_humans
两张表的可编辑字段；hasn-node daemon 的 `/api/v1/owner/me/profile`
代理直接转发到这里。
"""
from fastapi import APIRouter, Request

from backend.app.hasn.schema.profile import GetMergedProfile, UpdateMergedProfileParam
from backend.app.hasn.service.profile_service import hasn_profile_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/me', summary='获取合并 profile（sys_user + hasn_humans）', dependencies=[DependsJwtAuth])
async def get_my_merged_profile(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[GetMergedProfile]:
    data = await hasn_profile_service.get_merged(db=db, user_id=request.user.id)
    return response_base.success(data=data)


@router.put('/me', summary='更新合并 profile（事务内同时写两表）', dependencies=[DependsJwtAuth])
async def update_my_merged_profile(
    request: Request,
    db: CurrentSessionTransaction,
    obj: UpdateMergedProfileParam,
) -> ResponseSchemaModel[GetMergedProfile]:
    data = await hasn_profile_service.update_merged(db=db, user_id=request.user.id, obj=obj)
    return response_base.success(data=data)
