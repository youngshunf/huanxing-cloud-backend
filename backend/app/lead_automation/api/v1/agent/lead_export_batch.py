"""Lead CSV export batch - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.lead_automation.schema.lead_export_batch import (
    CreateLeadExportBatchParam,
    UpdateLeadExportBatchParam,
)
from backend.app.lead_automation.service.lead_export_batch_service import lead_export_batch_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Lead CSV export batch列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_lead_export_batchs(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await lead_export_batch_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Lead CSV export batch',
    dependencies=[DependsAgentAuth],
)
async def agent_create_lead_export_batch(
    db: CurrentSessionTransaction,
    obj: CreateLeadExportBatchParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await lead_export_batch_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Lead CSV export batch详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_lead_export_batch(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Lead CSV export batch ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_export_batch = await lead_export_batch_service.get(db=db, pk=pk)
    if lead_export_batch.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Lead CSV export batch')
    return response_base.success(data=lead_export_batch)


@router.put(
    '/{pk}',
    summary='更新Lead CSV export batch',
    dependencies=[DependsAgentAuth],
)
async def agent_update_lead_export_batch(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Lead CSV export batch ID')],
    obj: UpdateLeadExportBatchParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_export_batch = await lead_export_batch_service.get(db=db, pk=pk)
    if lead_export_batch.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Lead CSV export batch')
    count = await lead_export_batch_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Lead CSV export batch',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_lead_export_batch(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Lead CSV export batch ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_export_batch = await lead_export_batch_service.get(db=db, pk=pk)
    if lead_export_batch.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Lead CSV export batch')
    from backend.app.lead_automation.schema.lead_export_batch import DeleteLeadExportBatchParam
    count = await lead_export_batch_service.delete(db=db, obj=DeleteLeadExportBatchParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
