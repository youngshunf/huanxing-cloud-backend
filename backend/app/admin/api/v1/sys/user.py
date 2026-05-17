import hashlib
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, Path, Query, Request, UploadFile
from opendal import AsyncOperator

from backend.app.admin.schema.role import GetRoleDetail
from backend.app.admin.schema.user import (
    AddUserParam,
    GetCurrentUserInfoWithRelationDetail,
    GetUserInfoWithRelationDetail,
    ResetPasswordParam,
    UpdateUserParam,
    UpdateUserProfileParam,
)
from backend.app.admin.service.user_service import user_service
from backend.common.enums import UserPermissionType
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth, DependsSuperUser
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.common.exception import errors
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.s3.crud.storage import s3_storage_dao

router = APIRouter()


@router.get('/me', summary='获取当前用户信息', dependencies=[DependsJwtAuth])
async def get_current_user(request: Request) -> ResponseSchemaModel[GetCurrentUserInfoWithRelationDetail]:
    data = request.user.model_dump()
    return response_base.success(data=data)


@router.get('/{pk}', summary='获取用户信息', dependencies=[DependsJwtAuth])
async def get_userinfo(
    db: CurrentSession,
    pk: Annotated[int, Path(description='用户 ID')],
) -> ResponseSchemaModel[GetUserInfoWithRelationDetail]:
    data = await user_service.get_userinfo(db=db, pk=pk)
    return response_base.success(data=data)


@router.get('/{pk}/roles', summary='获取用户所有角色', dependencies=[DependsJwtAuth])
async def get_user_roles(
    db: CurrentSession, pk: Annotated[int, Path(description='用户 ID')]
) -> ResponseSchemaModel[list[GetRoleDetail]]:
    data = await user_service.get_roles(db=db, pk=pk)
    return response_base.success(data=data)


@router.get(
    '',
    summary='分页获取所有用户',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_users_paginated(
    db: CurrentSession,
    dept: Annotated[int | None, Query(description='部门 ID')] = None,
    username: Annotated[str | None, Query(description='用户名')] = None,
    phone: Annotated[str | None, Query(description='手机号')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
) -> ResponseSchemaModel[PageData[GetUserInfoWithRelationDetail]]:
    page_data = await user_service.get_list(db=db, dept=dept, username=username, phone=phone, status=status)
    return response_base.success(data=page_data)


@router.post('', summary='创建用户', dependencies=[DependsSuperUser])
async def create_user(
    db: CurrentSessionTransaction, obj: AddUserParam
) -> ResponseSchemaModel[GetUserInfoWithRelationDetail]:
    await user_service.create(db=db, obj=obj)
    data = await user_service.get_userinfo(db=db, username=obj.username)
    return response_base.success(data=data)


@router.put('/{pk}', summary='更新用户信息', dependencies=[DependsSuperUser])
async def update_user(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户 ID')],
    obj: UpdateUserParam,
) -> ResponseModel:
    count = await user_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/permissions', summary='更新用户权限', dependencies=[DependsSuperUser])
async def update_user_permission(
    db: CurrentSessionTransaction,
    request: Request,
    pk: Annotated[int, Path(description='用户 ID')],
    type: Annotated[UserPermissionType, Query(description='权限类型')],
) -> ResponseModel:
    count = await user_service.update_permission(db=db, request=request, pk=pk, type=type)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/password', summary='更新当前用户密码', dependencies=[DependsJwtAuth])
async def update_user_password(
    db: CurrentSessionTransaction, request: Request, obj: ResetPasswordParam
) -> ResponseModel:
    count = await user_service.update_password(db=db, user_id=request.user.id, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


# 短信验证码 Redis 前缀
SMS_CODE_PREFIX = 'sms_code'


@router.put('/me/password/sms', summary='通过短信验证码修改密码', dependencies=[DependsJwtAuth])
async def update_password_by_sms(
    db: CurrentSessionTransaction,
    request: Request,
    code: Annotated[str, Body(description='短信验证码')],
    new_password: Annotated[str, Body(description='新密码')],
    confirm_password: Annotated[str, Body(description='确认密码')],
) -> ResponseModel:
    """
    通过短信验证码修改密码
    
    - 需要先调用 /auth/phone/send-code 获取验证码
    - 验证码有效期 5 分钟
    """
    from backend.database.redis import redis_client
    from backend.app.admin.crud.crud_user import user_dao
    from backend.app.admin.service.user_password_history_service import password_security_service
    from backend.app.admin.utils.password_security import validate_new_password
    from backend.app.admin.schema.user_password_history import CreateUserPasswordHistoryParam
    from backend.core.conf import settings
    
    user = request.user
    phone = user.phone
    
    if not phone:
        raise errors.RequestError(msg='您的账号未绑定手机号，无法使用短信验证码修改密码')
    
    # 验证验证码
    stored_code = await redis_client.get(f'{SMS_CODE_PREFIX}:{phone}')
    if not stored_code:
        raise errors.RequestError(msg='验证码已过期，请重新获取')
    if stored_code != code:
        raise errors.RequestError(msg='验证码错误')
    
    # 删除已使用的验证码
    await redis_client.delete(f'{SMS_CODE_PREFIX}:{phone}')
    
    # 验证密码
    if new_password != confirm_password:
        raise errors.RequestError(msg='两次密码输入不一致')
    
    if len(new_password) < 6:
        raise errors.RequestError(msg='密码长度不能少于 6 位')
    
    # 验证新密码
    await validate_new_password(db, user.id, new_password)
    
    # 更新密码
    count = await user_dao.reset_password(db, user.id, new_password)
    
    # 保存密码历史
    user_obj = await user_dao.get(db, user.id)
    if user_obj and user_obj.password:
        history_obj = CreateUserPasswordHistoryParam(user_id=user.id, password=user_obj.password)
        await password_security_service.save_password_history(db, history_obj)
    await user_dao.update_password_changed_time(db, user.id)
    
    # 清除缓存
    key_prefix = [
        f'{settings.TOKEN_REDIS_PREFIX}:{user.id}',
        f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{user.id}',
        f'{settings.JWT_USER_REDIS_PREFIX}:{user.id}',
    ]
    for prefix in key_prefix:
        await redis_client.delete_prefix(prefix)
    
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/password', summary='重置用户密码', dependencies=[DependsSuperUser])
async def reset_user_password(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户 ID')],
    password: Annotated[str, Body(embed=True, description='新密码')],
) -> ResponseModel:
    count = await user_service.reset_password(db=db, pk=pk, password=password)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/nickname', summary='更新当前用户昵称', dependencies=[DependsJwtAuth])
async def update_user_nickname(
    db: CurrentSessionTransaction,
    request: Request,
    nickname: Annotated[str, Body(embed=True, description='用户昵称')],
) -> ResponseModel:
    count = await user_service.update_nickname(db=db, user_id=request.user.id, nickname=nickname)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/avatar', summary='更新当前用户头像', dependencies=[DependsJwtAuth])
async def update_user_avatar(
    db: CurrentSessionTransaction,
    request: Request,
    avatar: Annotated[str, Body(embed=True, description='用户头像地址')],
) -> ResponseModel:
    count = await user_service.update_avatar(db=db, user_id=request.user.id, avatar=avatar)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.post('/me/avatar/upload', summary='上传当前用户头像', dependencies=[DependsJwtAuth])
async def upload_user_avatar(
    db: CurrentSession,
    request: Request,
    file: Annotated[UploadFile, File(description='头像文件')],
) -> ResponseSchemaModel[dict]:
    """
    上传用户头像到 S3 存储
    
    支持的图片格式: jpg, jpeg, png, gif, webp
    最大文件大小: 5MB
    """
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise errors.RequestError(msg='不支持的图片格式，仅支持 jpg, png, gif, webp')
    
    # 验证文件大小
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise errors.RequestError(msg='文件大小不能超过 5MB')
    
    # 获取 S3 存储配置
    storages = await s3_storage_dao.get_all(db)
    s3_storage = storages[0] if storages else None
    if not s3_storage:
        raise errors.NotFoundError(
            msg='S3 存储配置不存在。请先在管理后台配置 S3 存储（系统管理 -> S3存储管理），'
            '或使用兼容 S3 的本地存储服务（如 MinIO）。'
        )
    
    # 创建 S3 操作器
    op = AsyncOperator(
        's3',
        endpoint=s3_storage.endpoint,
        access_key_id=s3_storage.access_key,
        secret_access_key=s3_storage.secret_key,
        bucket=s3_storage.bucket,
        root=s3_storage.prefix or '/',
        region=s3_storage.region or 'any',
    )
    
    # 生成文件名
    user_uuid = request.user.uuid
    file_ext = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'png'
    file_hash = hashlib.md5(content).hexdigest()[:8]
    filename = f'{user_uuid}_{file_hash}.{file_ext}'
    path = f'avatars/{filename}'
    
    # 上传文件
    try:
        await op.write(path, content)
    except Exception as e:
        raise errors.ServerError(msg=f'上传文件到 S3 失败: {str(e)}')

    # 构建 URL
    if s3_storage.cdn_domain:
        base_url = s3_storage.cdn_domain.rstrip('/')
        if s3_storage.prefix:
            prefix = s3_storage.prefix.strip('/')
            avatar_url = f'{base_url}/{prefix}/{path}'
        else:
            avatar_url = f'{base_url}/{path}'
    else:
        bucket_path = f'/{s3_storage.bucket}'
        if s3_storage.prefix:
            prefix = s3_storage.prefix if s3_storage.prefix.startswith('/') else f'/{s3_storage.prefix}'
            avatar_url = f'{s3_storage.endpoint}{bucket_path}{prefix}/{path}'
        else:
            avatar_url = f'{s3_storage.endpoint}{bucket_path}/{path}'
    
    return response_base.success(data={'url': avatar_url})


@router.put('/me/email', summary='更新当前用户邮箱', dependencies=[DependsJwtAuth])
async def update_user_email(
    db: CurrentSessionTransaction,
    request: Request,
    captcha: Annotated[str, Body(embed=True, description='邮箱验证码')],
    email: Annotated[str, Body(embed=True, description='用户邮箱')],
) -> ResponseModel:
    count = await user_service.update_email(db=db, user_id=request.user.id, captcha=captcha, email=email)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/me/profile', summary='更新当前用户资料', dependencies=[DependsJwtAuth])
async def update_user_profile(
    db: CurrentSessionTransaction,
    request: Request,
    obj: UpdateUserProfileParam,
) -> ResponseModel:
    count = await user_service.update_profile(db=db, user_id=request.user.id, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    path='/{pk}',
    summary='删除用户',
    dependencies=[
        Depends(RequestPermission('sys:user:del')),
        DependsRBAC,
    ],
)
async def delete_user(db: CurrentSessionTransaction, pk: Annotated[int, Path(description='用户 ID')]) -> ResponseModel:
    count = await user_service.delete(db=db, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
