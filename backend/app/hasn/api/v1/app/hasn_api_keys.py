from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.response.response_schema import ResponseModel, response_base
from backend.database.db import CurrentSession
from backend.app.hasn.schema.hasn_api_keys import CreateApiKeyReq, ApiKeyOut, CreateApiKeyRes
from backend.app.hasn.service.hasn_api_key_service import hasn_api_key_service
from backend.app.hasn.service.hasn_auth import hasn_auth_from_jwt

router = APIRouter()

@router.get('/api-keys', summary='获取节点 API Key 列表')
async def list_hasn_api_keys(
    db: CurrentSession,
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    clients = await hasn_api_key_service.list_api_keys(
        db=db,
        user_hasn_id=auth['hasn_id'],
    )
    return response_base.success(data=[
        ApiKeyOut(
            client_id=c.client_id,
            device_name=c.device_name,
            created_time=c.created_time,
            last_seen_at=c.last_seen_at,
        ).model_dump()
        for c in clients
    ])

@router.post('/api-keys', summary='生成新的 API Key')
async def create_hasn_api_key(
    obj_in: CreateApiKeyReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    result = await hasn_api_key_service.create_api_key(
        db=db,
        user_hasn_id=auth['hasn_id'],
        name=obj_in.name,
    )
    await db.commit()
    return response_base.success(data=result.model_dump())

@router.delete('/api-keys/{client_id}', summary='删除(吊销) API Key')
async def delete_hasn_api_key(
    client_id: str,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth_from_jwt),
) -> ResponseModel:
    await hasn_api_key_service.delete_api_key(
        db=db,
        user_hasn_id=auth['hasn_id'],
        client_id=client_id,
    )
    await db.commit()
    return response_base.success()
