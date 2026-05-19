from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.hasn.service.workbench_domain_service import workbench_domain_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction  # noqa: TC001

router = APIRouter()


@router.get('/workbench/workspaces/current/apps', dependencies=[DependsJwtAuth], summary='当前工作空间已挂载应用')
async def current_workspace_apps(request: Request, db: CurrentSessionTransaction) -> ResponseModel:
    apps = await workbench_domain_service.list_current_workspace_apps(db, user_id=request.user.id)
    return response_base.success(data=apps)


@router.get('/workbench/apps', dependencies=[DependsJwtAuth], summary='工作台应用市场')
async def list_workbench_apps(request: Request, db: CurrentSession, workspace_kind: str | None = None) -> ResponseModel:
    apps = await workbench_domain_service.list_workbench_apps(
        db,
        user_id=request.user.id,
        workspace_kind=workspace_kind,
    )
    return response_base.success(data=apps)


@router.post('/workbench/workspaces/current/apps/{app_id}', dependencies=[DependsJwtAuth], summary='挂载应用')
async def enable_workbench_app(request: Request, db: CurrentSessionTransaction, app_id: str) -> ResponseModel:
    data = await workbench_domain_service.enable_current_workspace_app(db, user_id=request.user.id, app_id=app_id)
    return response_base.success(data=data)


@router.delete('/workbench/workspaces/current/apps/{app_id}', dependencies=[DependsJwtAuth], summary='卸载应用')
async def disable_workbench_app(request: Request, db: CurrentSessionTransaction, app_id: str) -> ResponseModel:
    data = await workbench_domain_service.disable_current_workspace_app(db, user_id=request.user.id, app_id=app_id)
    return response_base.success(data=data)
