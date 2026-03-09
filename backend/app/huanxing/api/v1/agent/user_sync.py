"""唤星 Agent 用户同步 API

路径前缀: /api/v1/huanxing/agent/users
认证方式: X-Agent-Key（DependsAgentAuth）

供 Guardian Agent 在用户注册时同步用户信息到后端。
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.huanxing.schema.huanxing_user import AgentSyncUserParam, AgentUpdateUserParam
from backend.app.huanxing.service.huanxing_user_service import huanxing_user_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.database.db import CurrentSessionTransaction

router = APIRouter()


@router.post(
    '',
    summary='同步用户信息（注册时调用）',
    dependencies=[DependsAgentAuth],
)
async def agent_sync_user(
    db: CurrentSessionTransaction,
    obj: AgentSyncUserParam,
) -> ResponseModel:
    """Guardian Agent 注册新用户时调用，同步用户信息到后端。

    如果 agent_id 已存在则更新，否则创建新记录。
    """
    user = await huanxing_user_service.agent_sync(db=db, obj=obj)
    return response_base.success(data={
        'id': user.id if user else None,
        'agent_id': obj.agent_id,
        'synced': True,
    })


@router.put(
    '/{user_id}',
    summary='更新用户信息',
    dependencies=[DependsAgentAuth],
)
async def agent_update_user_info(
    db: CurrentSessionTransaction,
    user_id: Annotated[int, Path(description='平台用户 ID（sys_user.id）')],
    obj: AgentUpdateUserParam,
) -> ResponseModel:
    """Agent 更新用户信息（分身名字、模板、状态等）"""
    count = await huanxing_user_service.agent_update(db=db, user_id=user_id, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.success(data={'message': '无需更新'})
