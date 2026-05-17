"""HASN 用户搜索 API（IM MVP）

按唤星号精确匹配 + 昵称（name）前缀模糊匹配，返回当前用户与该 peer 的现有关系状态，
驱动前端"已是好友 / 已发送 / 可添加"的按钮态。
对应设计文档: docs/hasn-node设计文档/07-产品与端侧/05-消息模块.md §9.2 +
07-联系人模块.md §4 添加联系人入口。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.crud.crud_hasn_contacts import hasn_contacts_dao
from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn.service.hasn_auth import hasn_auth
from backend.common.response.response_schema import ResponseModel, response_base
from backend.database.db import CurrentSession


router = APIRouter(prefix="/users", tags=["HASN Users"])


@router.get("/search", summary="按唤星号或昵称搜索用户")
async def search_users(
    db: CurrentSession,
    q: str = Query(..., min_length=2, max_length=64, description="唤星号或昵称前缀"),
    limit: int = Query(20, ge=1, le=50, description="返回上限"),
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """搜索用户用于添加好友。

    匹配规则：
    1. 唤星号（star_id）精确命中：包含 `#` 时查 agents，否则查 humans。
    2. 昵称（name）前缀模糊匹配：仅 humans，case-insensitive。

    返回顺序：精确命中（如有）置顶，其余按 name 字典序。
    自己永远从结果剔除。每条携带 `existing_relation` 字段（pending|connected|archived|blocked|null），
    前端依此显示按钮态。
    """
    self_hasn_id: str = auth.get("effective_id", auth["hasn_id"])

    items: list[dict] = []
    seen: set[str] = set()

    # 1) 唤星号精确匹配
    if "#" in q:
        agent = await hasn_agents_dao.get_by_star_id(db, q)
        if agent and agent.hasn_id != self_hasn_id:
            items.append(_make_item(agent, peer_type="agent"))
            seen.add(agent.hasn_id)
    else:
        human = await hasn_humans_dao.get_by_star_id(db, q)
        if human and human.hasn_id != self_hasn_id:
            items.append(_make_item(human, peer_type="human"))
            seen.add(human.hasn_id)

    # 2) 昵称前缀模糊匹配（不与精确命中重复）
    if len(items) < limit:
        prefix_remaining = limit - len(items)
        humans = await hasn_humans_dao.search_by_name(
            db,
            prefix=q,
            limit=prefix_remaining + 1,  # +1 用于排除已 seen 后仍能取够 prefix_remaining
            exclude_hasn_id=self_hasn_id,
        )
        for h in humans:
            if h.hasn_id in seen:
                continue
            items.append(_make_item(h, peer_type="human"))
            seen.add(h.hasn_id)
            if len(items) >= limit:
                break

    # 3) 补 existing_relation
    for item in items:
        relation = await hasn_contacts_dao.get_relation(
            db, self_hasn_id, item["hasn_id"], "social",
        )
        item["existing_relation"] = relation.status if relation else None

    return response_base.success(data={"items": items, "total": len(items)})


def _make_item(entity, *, peer_type: str) -> dict:
    """把 HasnHumans / HasnAgents 行规范成搜索结果 item。"""
    return {
        "hasn_id": entity.hasn_id,
        "star_id": entity.star_id,
        "name": getattr(entity, "name", "") or "",
        "avatar": getattr(entity, "avatar", None),
        "type": peer_type,
        "existing_relation": None,
    }
