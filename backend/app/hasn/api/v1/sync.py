"""P0 HASN sync/runtime report endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.hasn.schema.hasn_sync import (
    MemorySyncPullRequest,
    MemorySyncPullResponse,
    RuntimeReportRequest,
    RuntimeReportResponse,
    SyncPullRequest,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
    TaskRunSummaryRequest,
)
from backend.app.hasn.service.hasn_sync_service import hasn_sync_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.post('/sync/pull', summary='Pull HASN sync events after cursor', dependencies=[DependsJwtAuth])
async def pull_sync_events(
    request: Request,
    db: CurrentSession,
    request_body: SyncPullRequest,
) -> SyncPullResponse:
    return await hasn_sync_service.pull(db, request_body, user_id=request.user.id)


@router.post('/sync/push', summary='Push HASN local client events', dependencies=[DependsJwtAuth])
async def push_sync_events(
    request: Request,
    db: CurrentSessionTransaction,
    request_body: SyncPushRequest,
) -> SyncPushResponse:
    return await hasn_sync_service.push(db, request_body, user_id=request.user.id)


@router.post('/tasks/sync/pull', summary='Pull HASN task sync events after task cursor', dependencies=[DependsJwtAuth])
async def pull_task_sync_events(
    request: Request,
    db: CurrentSession,
    request_body: SyncPullRequest,
) -> SyncPullResponse:
    request_body.node_id = request_body.node_id or request.headers.get('X-Node-Id')
    return await hasn_sync_service.pull_tasks(db, request_body, user_id=request.user.id)


@router.post('/tasks/sync/push', summary='Push HASN task client events', dependencies=[DependsJwtAuth])
async def push_task_sync_events(
    request: Request,
    db: CurrentSessionTransaction,
    request_body: SyncPushRequest,
) -> SyncPushResponse:
    return await hasn_sync_service.push_tasks(db, request_body, user_id=request.user.id)


@router.post('/tasks/runs/summary', summary='Report HASN task run summary', dependencies=[DependsAgentJwtAuth])
async def report_task_run_summary(
    request: Request,
    db: CurrentSessionTransaction,
    request_body: TaskRunSummaryRequest,
) -> ResponseModel:
    summary = await hasn_sync_service.report_task_run_summary(db, request_body, agent=request.state.agent)
    return response_base.success(data=summary)


@router.post(
    '/memory/sync/pull',
    summary='Pull HASN memory namespace events after namespace cursors',
    dependencies=[DependsJwtAuth],
)
async def pull_memory_sync_events(
    request: Request,
    db: CurrentSession,
    request_body: MemorySyncPullRequest,
) -> MemorySyncPullResponse:
    return await hasn_sync_service.pull_memory(db, request_body, user_id=request.user.id)


@router.post('/runtime/report', summary='Report redacted local Runtime status', dependencies=[DependsJwtAuth])
async def report_runtime(
    request: Request,
    db: CurrentSessionTransaction,
    request_body: RuntimeReportRequest,
) -> RuntimeReportResponse:
    return await hasn_sync_service.report_runtime(db, request_body, user_id=request.user.id)
