from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request

from backend.app.hasn.schema.ai_native_runtime import (
    AiNativeAuditQuery,
    AiNativeRuntimeCapabilitiesRequest,
    AiNativeToolCallRequest,
)
from backend.app.hasn.service.ai_native_app_registry import ai_native_app_registry
from backend.app.hasn.service.ai_native_audit_service import ai_native_audit_service
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
async def runtime_capabilities(request: Request, db: CurrentSession, body: AiNativeRuntimeCapabilitiesRequest) -> ResponseModel:
    manifest = await ai_native_app_registry.ensure_builtin_published(db, 'knowledge')
    tool = manifest['manifest_json']['tools'][0]
    agent = getattr(request.state, 'agent', None)
    return response_base.success(
        data={
            'workspace': body.workspace or {'kind': 'personal', 'user_id': None, 'enterprise_id': None, 'workspace_key': None},
            'agent': {
                'agent_hasn_id': getattr(agent, 'agent_hasn_id', None),
                'owner_hasn_id': getattr(agent, 'owner_hasn_id', None),
                'session_uuid': getattr(agent, 'session_uuid', None),
            },
            'manifest_hash': manifest['manifest_hash'],
            'tools': [
                {
                    'app_id': manifest['app_id'],
                    'tool_id': tool['tool_id'],
                    'mcp_name': tool['mcp_name'],
                    'collaboration_mode': manifest['collaboration_mode'],
                    'display_name': manifest['manifest_json']['capabilities'][0]['name'],
                    'input_schema': manifest['manifest_json']['capabilities'][0]['input_schema'],
                    'output_schema': manifest['manifest_json']['capabilities'][0]['output_schema'],
                    'required_scopes': tool['required_scopes'],
                    'risk_level': tool['risk_level'],
                    'requires_confirmation': False,
                    'idempotent': tool['idempotent'],
                }
            ],
        }
    )


@runtime_router.post('/tools/{app_id}/{tool_id}/call', summary='AI-Native Tool 调用', dependencies=[DependsAgentJwtAuth])
async def runtime_tool_call(
    request: Request,
    db: CurrentSessionTransaction,
    app_id: str,
    tool_id: str,
    body: AiNativeToolCallRequest,
) -> ResponseModel:
    manifest = await ai_native_app_registry.ensure_builtin_published(db, app_id)
    agent = getattr(request.state, 'agent', None)
    return response_base.success(
        data={
            'trace_id': body.trace_id,
            'decision': 'allow',
            'workspace': body.workspace or {'kind': 'personal', 'user_id': None, 'enterprise_id': None, 'workspace_key': None},
            'app_id': app_id,
            'tool_id': tool_id,
            'result': {'items': [], 'total': 0},
            'audit_id': manifest['id'],
            'agent': {
                'agent_hasn_id': getattr(agent, 'agent_hasn_id', None),
                'owner_hasn_id': getattr(agent, 'owner_hasn_id', None),
                'session_uuid': getattr(agent, 'session_uuid', None),
            },
        }
    )


@audit_router.get('', summary='AI-Native 审计')
async def list_ai_native_audit(db: CurrentSession, query: AiNativeAuditQuery) -> ResponseModel:
    return response_base.success(data=await ai_native_audit_service.get_list(db))
