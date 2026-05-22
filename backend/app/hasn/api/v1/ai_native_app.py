from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request

from backend.app.hasn.schema.ai_native_runtime import (
    AiNativeAuditQuery,
    AiNativeRuntimeCapabilitiesRequest,
    AiNativeToolCallRequest,
)
from backend.app.hasn.service.ai_native_app_registry import ai_native_app_registry
from backend.app.hasn.service.ai_native_runtime_gateway import ai_native_runtime_gateway
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

apps_router = APIRouter()
runtime_router = APIRouter()
audit_router = APIRouter()


@apps_router.get('', summary='AI-Native 应用清单')
async def list_ai_native_apps(db: CurrentSession) -> ResponseModel:
    return response_base.success(data=await ai_native_app_registry.list_published_manifests(db))


@apps_router.get('/{app_id}', summary='AI-Native 应用详情')
async def get_ai_native_app(db: CurrentSession, app_id: str) -> ResponseModel:
    return response_base.success(data=await ai_native_app_registry.get(db, app_id))


@apps_router.post('/{app_id}/validate', summary='AI-Native 应用校验')
async def validate_ai_native_app(db: CurrentSession, app_id: str, body: dict[str, Any]) -> ResponseModel:
    result = ai_native_app_registry.validate_manifest(body)
    return response_base.success(
        data={
            'app_id': app_id,
            'valid': result.valid,
            'errors': result.errors,
            'manifest_hash': result.manifest_hash,
        }
    )


@apps_router.post('/{app_id}/publish', summary='AI-Native 应用发布')
async def publish_ai_native_app(db: CurrentSessionTransaction, app_id: str) -> ResponseModel:
    return response_base.success(data=await ai_native_app_registry.publish_builtin(db, app_id))


@runtime_router.post('/capabilities', summary='AI-Native 能力发现', dependencies=[DependsAgentJwtAuth])
async def runtime_capabilities(
    request: Request, db: CurrentSession, body: AiNativeRuntimeCapabilitiesRequest
) -> ResponseModel:
    data = await ai_native_runtime_gateway.get_capabilities(db=db, request=request, body=body)
    return response_base.success(data=data)


@runtime_router.post(
    '/tools/{app_id}/{tool_id}/call',
    summary='AI-Native Tool 调用',
)
async def runtime_tool_call(
    request: Request,
    db: CurrentSessionTransaction,
    app_id: str,
    tool_id: str,
    body: AiNativeToolCallRequest,
) -> ResponseModel:
    data = await ai_native_runtime_gateway.call_tool(db=db, request=request, app_id=app_id, tool_id=tool_id, body=body)
    return response_base.success(data=data)


@audit_router.get('', summary='AI-Native 审计')
async def list_ai_native_audit(db: CurrentSession, query: AiNativeAuditQuery = Depends()) -> ResponseModel:
    return response_base.success(data=await ai_native_runtime_gateway.list_audit(db=db, query=query))
