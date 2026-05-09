"""联系人模块 P1: GET /api/v1/hasn/app/contacts/requests?direction=...

覆盖路由层逻辑:
- direction=received (默认) 行为不变 (回归保护)
- direction=sent 走新 DAO + target 字段
- A 发 B 收, 两边查询互不串
- direction 非法返回 422

DAO 全部 mock。HasnContacts 用 PostgreSQL JSONB 在 SQLite 上跑不起来,
因此本测试只验路由组装与字段映射。
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from backend.app.hasn.api.v1.app.contacts import list_pending_requests


SELF = "h_aaaaaaaaaaaaaaaaaa"
PEER = "h_bbbbbbbbbbbbbbbbbb"


def _human(hasn_id: str, star_id: str, name: str) -> SimpleNamespace:
    return SimpleNamespace(hasn_id=hasn_id, star_id=star_id, name=name)


def _request(req_id: int, owner_id: str, peer_id: str, message: str = '') -> SimpleNamespace:
    return SimpleNamespace(
        id=req_id,
        owner_id=owner_id,
        peer_id=peer_id,
        status='pending',
        request_message=message,
    )


@pytest.mark.asyncio
async def test_received_default_unchanged() -> None:
    """direction='received' 走旧 received 路径, 旧 daemon 调用照常工作。"""
    with patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_pending_requests',
        new=AsyncMock(return_value=[_request(101, PEER, SELF, '想加个好友')]),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=_human(PEER, '100002', 'Bob')),
    ):
        resp = await list_pending_requests(
            db=AsyncMock(),
            auth={'hasn_id': SELF},
            direction='received',
        )
    items = resp.data
    assert len(items) == 1
    assert items[0]['request_id'] == 101
    assert items[0]['from_peer']['hasn_id'] == PEER
    assert items[0]['from_peer']['name'] == 'Bob'
    # sent 路径不应被触发, 因此 target 应为 None
    assert items[0]['target'] is None
    assert items[0]['message'] == '想加个好友'


@pytest.mark.asyncio
async def test_sent_direction_returns_target() -> None:
    """direction=sent 走 get_sent_pending_requests + target 字段。"""
    with patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_sent_pending_requests',
        new=AsyncMock(return_value=[_request(202, SELF, PEER)]),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=_human(PEER, '100002', 'Bob')),
    ):
        resp = await list_pending_requests(
            db=AsyncMock(),
            auth={'hasn_id': SELF},
            direction='sent',
        )
    items = resp.data
    assert len(items) == 1
    assert items[0]['request_id'] == 202
    assert items[0]['target']['hasn_id'] == PEER
    assert items[0]['target']['name'] == 'Bob'
    # received 路径不应被触发
    assert items[0]['from_peer'] is None


@pytest.mark.asyncio
async def test_sent_and_received_dont_cross() -> None:
    """A 发给 B: A 看到 sent, B 看到 received, 互不串。"""
    with patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_sent_pending_requests',
        new=AsyncMock(return_value=[_request(303, SELF, PEER)]),
    ) as mock_sent, patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_pending_requests',
        new=AsyncMock(return_value=[]),
    ) as mock_received, patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=_human(PEER, '100002', 'Bob')),
    ):
        resp_sent = await list_pending_requests(
            db=AsyncMock(),
            auth={'hasn_id': SELF},
            direction='sent',
        )
        resp_received = await list_pending_requests(
            db=AsyncMock(),
            auth={'hasn_id': SELF},
            direction='received',
        )
    assert mock_sent.await_count == 1
    assert mock_received.await_count == 1
    assert len(resp_sent.data) == 1
    assert resp_sent.data[0]['request_id'] == 303
    assert resp_received.data == []


@pytest.mark.asyncio
async def test_invalid_direction_raises_422() -> None:
    """direction 既非 received 也非 sent, 返回 422。"""
    with pytest.raises(HTTPException) as exc:
        await list_pending_requests(
            db=AsyncMock(),
            auth={'hasn_id': SELF},
            direction='garbage',
        )
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_sent_peer_resolution_falls_back_to_stub() -> None:
    """peer_id 解析失败时返回 stub 占位, 不抛 500 (INV-15)。"""
    with patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_sent_pending_requests',
        new=AsyncMock(return_value=[_request(404, SELF, 'h_unknownxxxxxxxxxx')]),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=None),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_agents_dao.get_by_hasn_id',
        new=AsyncMock(return_value=None),
    ):
        resp = await list_pending_requests(
            db=AsyncMock(),
            auth={'hasn_id': SELF},
            direction='sent',
        )
    assert len(resp.data) == 1
    assert resp.data[0]['target']['hasn_id'] == 'h_unknownxxxxxxxxxx'
    # 解析失败时 stub 用空串 (schema 要求 str), 不是 None
    assert resp.data[0]['target']['name'] == ''
    assert resp.data[0]['target']['star_id'] == ''
