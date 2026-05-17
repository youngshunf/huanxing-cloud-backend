"""HASN 用户端合并 profile API.

`GET/PUT /api/v1/hasn/app/profile/me` — 合并 sys_user + hasn_humans
两张表的可编辑字段；hasn-node daemon 的 `/api/v1/owner/me/profile`
代理直接转发到这里。
"""
from fastapi import APIRouter, Query, Request
from sqlalchemy import select

from backend.app.admin.model.user import User
from backend.app.hasn.model.hasn_humans import HasnHumans
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


@router.get('/check-nickname', summary='检查昵称是否可用', dependencies=[DependsJwtAuth])
async def check_nickname_availability(
    request: Request,
    db: CurrentSession,
    nickname: str = Query(..., min_length=1, max_length=40, description='要检查的昵称'),
) -> ResponseSchemaModel[dict]:
    """
    检查昵称是否可用（唯一性校验）

    返回：
    - available: bool - 是否可用
    - reason: str | None - 不可用原因（'taken' | 'invalid' | 'reserved'）
    - message: str - 提示信息
    """
    # 去除首尾空格
    nickname = nickname.strip()

    # 基础校验
    if not nickname or len(nickname) > 40:
        return response_base.success(
            data={'available': False, 'reason': 'invalid', 'message': '昵称长度必须在 1-40 个字符之间'}
        )

    # 保留词检查
    reserved_words = ['admin', 'system', 'hasn', 'huanxing', 'root']
    if nickname.lower() in reserved_words:
        return response_base.success(
            data={'available': False, 'reason': 'reserved', 'message': '该昵称为系统保留，请选择其他昵称'}
        )

    # 检查 sys_user 表
    user_result = await db.execute(
        select(User.id).where(User.nickname == nickname, User.id != request.user.id).limit(1)
    )
    if user_result.scalar_one_or_none():
        return response_base.success(
            data={'available': False, 'reason': 'taken', 'message': '该昵称已被使用，请选择其他昵称'}
        )

    # 检查 hasn_humans 表
    human_result = await db.execute(
        select(HasnHumans.id).where(HasnHumans.nickname == nickname, HasnHumans.user_id != request.user.id).limit(1)
    )
    if human_result.scalar_one_or_none():
        return response_base.success(
            data={'available': False, 'reason': 'taken', 'message': '该昵称已被使用，请选择其他昵称'}
        )

    return response_base.success(data={'available': True, 'reason': None, 'message': '昵称可用'})


@router.get('/preset-avatars', summary='获取预置头像列表')
async def get_preset_avatars() -> ResponseSchemaModel[list[dict]]:
    """
    返回预置头像列表（无需认证）

    返回格式：
    [
        {"id": "avatar-01", "url": "/avatars/preset/avatar-01.svg"},
        {"id": "avatar-02", "url": "/avatars/preset/avatar-02.svg"},
        ...
    ]
    """
    # 预置头像列表（12 个）
    preset_avatars = [{'id': f'avatar-{i:02d}', 'url': f'/avatars/preset/avatar-{i:02d}.svg'} for i in range(1, 13)]

    return response_base.success(data=preset_avatars)
