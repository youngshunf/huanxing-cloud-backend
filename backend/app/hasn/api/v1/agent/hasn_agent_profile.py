"""HASN Agent Profile - Agent 端 API（云端权威化）

认证方式: DependsAgentJwtAuth（Agent JWT）
身份: **恒取自 JWT**（agent.agent_hasn_id），绝不从请求体/路径读取身份字段。

Runtime（huanxing-hermes-runtime）用 agent JWT 直连这里拉取自己 Agent 的 Profile，
物化为本地 SOUL.md/AGENTS.md/USER.md/MEMORY.md + 按 skills 清单下载技能包。
见 decisions/architecture/2026-05-30-agent-profile-cloud-authoritative.md §5.2。
"""

from typing import Annotated, Any

import sqlalchemy as sa

from fastapi import APIRouter

from backend.app.hasn.model import HasnAgents
from backend.app.hasn.schema.hasn_agents import (
    AgentProfileResponse,
    AgentProfileRevisionResponse,
)
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


def _normalize_skill_ids(skills: Any) -> list[str]:
    """把 hasn_agents.skills（JSONB）归一化为 skill_id 字符串清单。

    兼容三种历史形态：list[str] / list[{skill_id|id}] / {skill_id: version}。
    """
    if skills is None:
        return []
    if isinstance(skills, list):
        out: list[str] = []
        for item in skills:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
            elif isinstance(item, dict):
                sid = item.get('skill_id') or item.get('id')
                if sid:
                    out.append(str(sid))
        return out
    if isinstance(skills, dict):
        return [str(key) for key in skills if key]
    return []


@router.get(
    '/profile',
    summary='Agent 直连拉取自己的 Profile（云端权威）',
)
async def get_agent_profile(
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    db: CurrentSession,
) -> ResponseSchemaModel[AgentProfileResponse]:
    row = (
        await db.execute(sa.select(HasnAgents).where(HasnAgents.hasn_id == agent.agent_hasn_id).limit(1))
    ).scalar_one_or_none()
    if row is None:
        raise errors.NotFoundError(msg='ERR_HASN_AGENT_NOT_FOUND')

    return response_base.success(
        data=AgentProfileResponse(
            hasn_id=row.hasn_id,
            display_name=row.display_name,
            soul_md=row.soul_md,
            agents_md=getattr(row, 'agents_md', None),
            user_md=row.user_md,
            memory_md=getattr(row, 'memory_md', None),
            skills=_normalize_skill_ids(getattr(row, 'skills', None)),
            template_id=row.template_id,
            template_version=getattr(row, 'template_version', None),
            profile_revision=int(getattr(row, 'profile_revision', 1) or 1),
        )
    )


@router.get(
    '/profile/revision',
    summary='Agent 轮询自己的 Profile 修订号（轻量，用于记忆下发检测）',
)
async def get_agent_profile_revision(
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    db: CurrentSession,
) -> ResponseSchemaModel[AgentProfileRevisionResponse]:
    rev = (
        await db.execute(
            sa.select(HasnAgents.profile_revision).where(HasnAgents.hasn_id == agent.agent_hasn_id).limit(1)
        )
    ).scalar_one_or_none()
    if rev is None:
        raise errors.NotFoundError(msg='ERR_HASN_AGENT_NOT_FOUND')
    return response_base.success(data=AgentProfileRevisionResponse(profile_revision=int(rev or 1)))
