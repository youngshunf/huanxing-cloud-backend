"""联系人模块 P-A: 好友请求 / 通过 走 WS push.

覆盖:
- POST /contacts/request 调用 ws_router.push_message_to(target, hasn.contact.request_received)
- PUT /contacts/requests/{id}/respond accept 调用 ws_router.push_message_to(owner, hasn.contact.connected)
- WS push 失败时 HTTP 仍然成功 (best-effort, 不阻塞主链路)

DAO 全部 mock 以保持 SQLite 跑得起来 (HasnContacts 是 JSONB).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.app.hasn.api.v1.app.contacts import (
    respond_to_request,
    send_contact_request,
)
from backend.app.hasn.schema.hasn_contacts_business import (
    HasnContactRequestReq,
    HasnContactRespondReq,
)


SENDER = "h_aaaaaaaaaaaaaaaaaa"
RECEIVER = "h_bbbbbbbbbbbbbbbbbb"
RECEIVER_AGENT = "a_bbbbbbbbbbbbbbbbbb"
SENDER_STAR = "100001"
RECEIVER_STAR = "100002"
RECEIVER_AGENT_STAR = "100002#helper"


def _human(hasn_id: str, star_id: str, name: str) -> SimpleNamespace:
    return SimpleNamespace(hasn_id=hasn_id, star_id=star_id, name=name)


def _agent(hasn_id: str, star_id: str, name: str, owner_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        hasn_id=hasn_id,
        star_id=star_id,
        display_name=name,
        name=name,
        owner_id=owner_id,
    )


def _contact(req_id: int, owner_id: str, peer_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=req_id,
        owner_id=owner_id,
        peer_id=peer_id,
        status='pending',
        request_message='',
    )


@pytest.mark.asyncio
async def test_send_request_pushes_request_received_to_target() -> None:
    """A 发好友请求给 B → 后端推 hasn.contact.request_received 给 B."""
    receiver = _human(RECEIVER, RECEIVER_STAR, 'Bob')
    sender = _human(SENDER, SENDER_STAR, 'Alice')
    push = AsyncMock(return_value=True)

    with patch(
        'backend.app.hasn.api.v1.app.contacts._resolve_star_id',
        new=AsyncMock(return_value=(receiver, 'human')),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_relation',
        new=AsyncMock(return_value=None),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.create_contact',
        new=AsyncMock(return_value=_contact(42, SENDER, RECEIVER)),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=sender),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to',
        new=push,
    ):
        db = AsyncMock()
        await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=RECEIVER_STAR, message='hi'),
            db=db,
            auth={'hasn_id': SENDER},
        )

    push.assert_awaited_once()
    target, payload = push.await_args.args
    assert target == RECEIVER
    assert payload['method'] == 'hasn.contact.request_received'
    assert payload['params']['owner_id'] == RECEIVER  # daemon 用 owner_id 路由 ws sink
    assert payload['params']['request_id'] == 42
    assert payload['params']['from_peer']['hasn_id'] == SENDER
    assert payload['params']['from_peer']['star_id'] == SENDER_STAR
    assert payload['params']['message'] == 'hi'


@pytest.mark.asyncio
async def test_send_agent_request_pushes_request_received_to_agent_owner() -> None:
    """A 请求添加 B 的 Agent → 后端推 hasn.contact.request_received 给 B, 不是给 Agent ID."""
    receiver_agent = _agent(RECEIVER_AGENT, RECEIVER_AGENT_STAR, 'Bob Helper', RECEIVER)
    sender = _human(SENDER, SENDER_STAR, 'Alice')
    push = AsyncMock(return_value=True)

    with patch(
        'backend.app.hasn.api.v1.app.contacts._resolve_star_id',
        new=AsyncMock(return_value=(receiver_agent, 'agent')),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_relation',
        new=AsyncMock(return_value=None),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.create_contact',
        new=AsyncMock(return_value=_contact(43, SENDER, RECEIVER_AGENT)),
    ) as create_contact, patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=sender),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to',
        new=push,
    ):
        db = AsyncMock()
        await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=RECEIVER_AGENT_STAR, message='hi agent'),
            db=db,
            auth={'hasn_id': SENDER},
        )

    create_contact.assert_awaited_once()
    assert create_contact.await_args.kwargs['peer_id'] == RECEIVER_AGENT
    assert create_contact.await_args.kwargs['peer_type'] == 'agent'
    assert create_contact.await_args.kwargs['peer_owner_id'] == RECEIVER

    push.assert_awaited_once()
    target, payload = push.await_args.args
    assert target == RECEIVER
    assert payload['method'] == 'hasn.contact.request_received'
    assert payload['params']['owner_id'] == RECEIVER
    assert payload['params']['request_id'] == 43
    assert payload['params']['from_peer']['hasn_id'] == SENDER
    assert payload['params']['target']['hasn_id'] == RECEIVER_AGENT
    assert payload['params']['target']['type'] == 'agent'


@pytest.mark.asyncio
async def test_respond_accept_pushes_connected_to_original_owner() -> None:
    """B 通过 A 的请求 → 后端推 hasn.contact.connected 给 A (owner_id)."""
    contact = _contact(42, SENDER, RECEIVER)
    acceptor = _human(RECEIVER, RECEIVER_STAR, 'Bob')
    push = AsyncMock(return_value=True)

    with patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.accept_request',
        new=AsyncMock(),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get',
        new=AsyncMock(return_value=contact),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_relation',
        new=AsyncMock(return_value=None),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.create_contact',
        new=AsyncMock(),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=acceptor),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to',
        new=push,
    ):
        db = AsyncMock()
        await respond_to_request(
            request_id=42,
            obj_in=HasnContactRespondReq(action='accept'),
            db=db,
            auth={'hasn_id': RECEIVER},
        )

    push.assert_awaited_once()
    target, payload = push.await_args.args
    assert target == SENDER  # 推给原发起方,不是 acceptor
    assert payload['method'] == 'hasn.contact.connected'
    assert payload['params']['owner_id'] == SENDER  # daemon 用 owner_id 路由 ws sink
    assert payload['params']['request_id'] == 42
    assert payload['params']['peer']['hasn_id'] == RECEIVER
    assert payload['params']['peer']['name'] == 'Bob'
    assert payload['params']['trust_level'] == 2


@pytest.mark.asyncio
async def test_respond_reject_does_not_push() -> None:
    """B 拒绝 → 不推任何 ws (rejected 状态发起方下次轮询自然能查到)."""
    push = AsyncMock(return_value=True)
    with patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.reject_request',
        new=AsyncMock(),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to',
        new=push,
    ):
        db = AsyncMock()
        await respond_to_request(
            request_id=42,
            obj_in=HasnContactRespondReq(action='reject'),
            db=db,
            auth={'hasn_id': RECEIVER},
        )
    push.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_request_succeeds_even_if_ws_push_fails() -> None:
    """WS push 抛异常时 HTTP 仍然 success (fail-open, 不阻塞主链路)."""
    receiver = _human(RECEIVER, RECEIVER_STAR, 'Bob')
    sender = _human(SENDER, SENDER_STAR, 'Alice')

    with patch(
        'backend.app.hasn.api.v1.app.contacts._resolve_star_id',
        new=AsyncMock(return_value=(receiver, 'human')),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.get_relation',
        new=AsyncMock(return_value=None),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_contacts_dao.create_contact',
        new=AsyncMock(return_value=_contact(42, SENDER, RECEIVER)),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.hasn_humans_dao.get_by_hasn_id',
        new=AsyncMock(return_value=sender),
    ), patch(
        'backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to',
        new=AsyncMock(side_effect=RuntimeError('redis unreachable')),
    ):
        db = AsyncMock()
        resp = await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=RECEIVER_STAR, message='hi'),
            db=db,
            auth={'hasn_id': SENDER},
        )

    # response_base.success 包了一层. 关键: 没炸即可.
    assert resp.data['request_id'] == 42
    assert resp.data['status'] == 'pending'
