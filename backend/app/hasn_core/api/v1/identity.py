"""
HASN Profile & 搜索 API
对应设计文档: 07-API设计.md §二
"""
from fastapi import APIRouter, Depends, Query

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.response.response_code import CustomResponse
from backend.database.db import CurrentSession
from backend.app.hasn_core.service.hasn_auth import hasn_auth
from backend.app.hasn_core.crud.crud_human import crud_hasn_human
from backend.app.hasn_core.crud.crud_agent import crud_hasn_agent
from backend.app.hasn_core.schema.hasn_identity import (
    HasnProfileUpdateReq, HasnProfileOut,
    HasnSearchResultItem, HasnSearchResp,
)

router = APIRouter(prefix="/identity", tags=["HASN Identity"])


@router.get("/me", summary="获取当前身份信息")
async def get_me(
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    entity_type = auth["type"]

    if entity_type == "human":
        human = await crud_hasn_human.get_by_id(db, hasn_id)
        if not human:
            return response_base.fail(res=CustomResponse(code=400, msg="用户不存在"))
        agents = await crud_hasn_agent.get_by_owner_id(db, hasn_id)
        return response_base.success(data=HasnProfileOut(
            hasn_id=human.id,
            star_id=human.star_id,
            type="human",
            name=human.name,
            bio=human.bio,
            avatar_url=human.avatar_url,
            status=human.status,
            agents_count=len(agents),
        ).model_dump())
    else:
        agent = await crud_hasn_agent.get_by_id(db, hasn_id)
        if not agent:
            return response_base.fail(res=CustomResponse(code=400, msg="Agent 不存在"))
        return response_base.success(data=HasnProfileOut(
            hasn_id=agent.id,
            star_id=agent.star_id,
            type="agent",
            name=agent.name,
            bio=agent.description,
            status=agent.status,
        ).model_dump())


@router.put("/profile", summary="更新个人资料")
async def update_profile(
    obj_in: HasnProfileUpdateReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    human = await crud_hasn_human.get_by_id(db, hasn_id)
    if not human:
        return response_base.fail(res=CustomResponse(code=400, msg="用户不存在"))

    if obj_in.name is not None:
        human.name = obj_in.name
    if obj_in.bio is not None:
        human.bio = obj_in.bio
    if obj_in.avatar_url is not None:
        human.avatar_url = obj_in.avatar_url
    await db.commit()
    return response_base.success(data={"hasn_id": hasn_id, "updated": True})


@router.get("/profile/{star_id}", summary="查看他人公开资料")
async def get_profile(
    star_id: str,
    db: CurrentSession,
) -> ResponseModel:
    """不需要认证，公开接口"""
    entity = await crud_hasn_human.get_by_star_id(db, star_id)
    entity_type = "human"
    if not entity:
        entity = await crud_hasn_agent.get_by_star_id(db, star_id)
        entity_type = "agent"
    if not entity:
        return response_base.fail(res=CustomResponse(code=400, msg=f"唤星号 {star_id} 不存在"))

    bio = entity.bio if entity_type == "human" else getattr(entity, 'description', '')
    return response_base.success(data=HasnProfileOut(
        hasn_id=entity.id,
        star_id=entity.star_id,
        type=entity_type,
        name=entity.name,
        bio=bio,
        avatar_url=getattr(entity, 'avatar_url', None),
        status=entity.status,
    ).model_dump())


@router.get("/search", summary="搜索用户/Agent")
async def hasn_search(
    db: CurrentSession,
    q: str = Query(..., min_length=1, description="搜索关键词"),
    type: str = Query("star_id", description="搜索类型: star_id / name"),
    limit: int = Query(10, ge=1, le=50),
) -> ResponseModel:
    """不需要认证，公开接口"""
    items = []

    if type == "star_id":
        # 精确匹配 human
        human = await crud_hasn_human.get_by_star_id(db, q)
        if human:
            agents = await crud_hasn_agent.get_by_owner_id(db, human.id)
            items.append(HasnSearchResultItem(
                star_id=human.star_id,
                name=human.name,
                type="human",
                avatar_url=human.avatar_url,
                bio=human.bio,
                agents_count=len(agents),
            ))
        # 精确匹配 agent
        agent = await crud_hasn_agent.get_by_star_id(db, q)
        if agent:
            items.append(HasnSearchResultItem(
                star_id=agent.star_id,
                name=agent.name,
                type="agent",
                bio=agent.description,
            ))

    elif type == "name":
        humans = await crud_hasn_human.search_by_name(db, q, limit=limit)
        for h in humans:
            items.append(HasnSearchResultItem(
                star_id=h.star_id,
                name=h.name,
                type="human",
                avatar_url=h.avatar_url,
                bio=h.bio,
            ))

    return response_base.success(data=HasnSearchResp(
        total=len(items),
        items=items,
    ).model_dump())
