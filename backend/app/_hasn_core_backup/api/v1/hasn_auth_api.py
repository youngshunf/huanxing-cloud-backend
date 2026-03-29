"""HASN 认证与客户端注册 REST API

端点：
- POST /hasn/auth/register          注册 HASN 身份（Human + 默认 Agent）
- POST /hasn/auth/register-client   注册客户端设备
- POST /hasn/auth/client-token      签发 Client JWT
- GET  /hasn/me                     获取当前用户 HASN 身份
- GET  /hasn/me/clients             我的客户端列表
- GET  /hasn/me/agents              我的 Agent 列表（含在线状态）
"""

from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth, jwt_authentication
from backend.database.db import CurrentSession, async_db_session
from backend.app.hasn_core.model import HasnHumans
from backend.app.hasn_core.model.hasn_agents import HasnAgents
from backend.app.hasn_core.model.hasn_clients import HasnClients
from backend.app.hasn_core.service.hasn_auth import (
    register_hasn_identity,
    register_client,
    issue_client_jwt,
    hasn_auth_from_jwt,
)
from backend.app.hasn_core.service.ws_router import ws_router

router = APIRouter()


# ─── 请求/响应模型 ───

class RegisterHasnReq(BaseModel):
    name: str = Field(description='显示名称')
    bio: str | None = Field(None, description='个人简介')
    avatar_url: str | None = Field(None, description='头像 URL')


class RegisterClientReq(BaseModel):
    client_type: str = Field(default='desktop', description='客户端类型: desktop/mobile/web')
    device_name: str | None = Field(None, description='设备名称')
    device_info: dict | None = Field(None, description='设备信息')


# ─── 注册 HASN 身份 ───

@router.post('/auth/register', summary='注册 HASN 身份')
async def api_register_hasn(
    obj_in: RegisterHasnReq,
    db: CurrentSession,
    _token: str = DependsJwtAuth,
    request: Request = None,
) -> ResponseModel:
    """为当前平台用户注册 HASN 身份（Human + 默认 Agent）"""
    # 从平台 JWT 获取 user_id
    authorization = request.headers.get('Authorization', '')
    token = authorization.replace('Bearer ', '')
    user_info = await jwt_authentication(token)

    result = await register_hasn_identity(
        db=db,
        user_id=user_info.id,
        name=obj_in.name,
        avatar_url=obj_in.avatar_url,
        bio=obj_in.bio,
    )
    await db.commit()

    return await response_base.success(data={
        'human': {
            'hasn_id': result['human'].hasn_id,
            'star_id': result['human'].star_id,
            'name': result['human'].name,
        },
        'agent': {
            'hasn_id': result['agent'].hasn_id,
            'star_id': result['agent'].star_id,
            'name': result['agent'].name,
            'api_key': result['api_key'],
        },
    })


# ─── 注册客户端 ───

@router.post('/auth/register-client', summary='注册客户端设备')
async def api_register_client(
    obj_in: RegisterClientReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    """注册客户端设备，返回 client_id"""
    client = await register_client(
        db=db,
        user_hasn_id=auth['hasn_id'],
        client_type=obj_in.client_type,
        device_name=obj_in.device_name,
        device_info=obj_in.device_info,
    )
    await db.commit()

    return await response_base.success(data={
        'client_id': client.client_id,
        'client_type': client.client_type,
        'device_name': client.device_name,
    })


class ClientTokenReq(BaseModel):
    client_id: str = Field(description='客户端 ID')


# ─── 签发 Client JWT ───

@router.post('/auth/client-token', summary='签发 Client JWT')
async def api_client_token(
    obj_in: ClientTokenReq,
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    """签发 Client JWT（用于 WebSocket 连接认证）"""
    client_id = obj_in.client_id
    # 验证 client_id 归属当前用户
    async with async_db_session() as db:
        result = await db.execute(
            select(HasnClients).where(
                HasnClients.client_id == client_id,
                HasnClients.user_hasn_id == auth['hasn_id'],
                HasnClients.status == 'active',
            )
        )
        client = result.scalar_one_or_none()

    if not client:
        return await response_base.fail(msg='客户端不存在或不属于当前用户')

    token = issue_client_jwt(
        user_hasn_id=auth['hasn_id'],
        client_id=client_id,
        client_type=client.client_type,
        star_id=auth['star_id'],
    )

    return await response_base.success(data={
        'client_jwt': token,
        'client_id': client_id,
    })


# ─── 获取当前用户 HASN 身份 ───

@router.get('/me', summary='获取当前用户 HASN 身份')
async def api_get_me(
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    """获取当前用户的 HASN 身份信息"""
    async with async_db_session() as db:
        result = await db.execute(
            select(HasnHumans).where(HasnHumans.hasn_id == auth['hasn_id'])
        )
        human = result.scalar_one_or_none()

    if not human:
        return await response_base.fail(msg='HASN 身份不存在')

    return await response_base.success(data={
        'hasn_id': human.hasn_id,
        'star_id': human.star_id,
        'name': human.name,
        'bio': human.bio,
        'avatar_url': human.avatar_url,
        'status': human.status,
        'contact_policy': human.contact_policy,
        'timezone': human.timezone,
        'tags': human.tags,
        'stats': human.stats,
    })


# ─── 我的客户端列表 ───

@router.get('/me/clients', summary='我的客户端列表')
async def api_list_clients(
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    """查询当前用户的所有客户端设备"""
    async with async_db_session() as db:
        result = await db.execute(
            select(HasnClients).where(
                HasnClients.user_hasn_id == auth['hasn_id'],
                HasnClients.status == 'active',
            ).order_by(HasnClients.created_time.desc())
        )
        clients = result.scalars().all()

    return await response_base.success(data=[
        {
            'client_id': c.client_id,
            'client_type': c.client_type,
            'device_name': c.device_name,
            'device_info': c.device_info,
            'last_seen_at': c.last_seen_at.isoformat() if c.last_seen_at else None,
            'created_time': c.created_time.isoformat() if c.created_time else None,
        }
        for c in clients
    ])


# ─── 我的 Agent 列表 ───

@router.get('/me/agents', summary='我的 Agent 列表')
async def api_list_agents(
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    """查询当前用户的所有 Agent（含在线状态）"""
    async with async_db_session() as db:
        result = await db.execute(
            select(HasnAgents).where(
                HasnAgents.owner_id == auth['hasn_id'],
                HasnAgents.status == 'active',
            ).order_by(HasnAgents.created_time.desc())
        )
        agents = result.scalars().all()

    agents_data = []
    for a in agents:
        online = await ws_router.is_agent_online(a.hasn_id)
        agents_data.append({
            'hasn_id': a.hasn_id,
            'star_id': a.star_id,
            'name': a.name,
            'agent_name': a.agent_name,
            'type': a.type,
            'server_id': a.server_id,
            'online': online,
            'created_via': a.created_via,
            'created_time': a.created_time.isoformat() if a.created_time else None,
        })

    return await response_base.success(data=agents_data)
