"""P0 HASN S4 message hub endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from backend.app.hasn.schema.hasn_message_hub import (
    InboxPullRequest,
    InboxPullResponse,
    MessageHubSendRequest,
    MessageHubSendResponse,
)
from backend.app.hasn.service.hasn_message_hub_service import hasn_message_hub_service
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.post(
    '/messages/send',
    summary='Send a HASN message through cloud message hub',
    dependencies=[DependsJwtAuth],
)
async def send_message(
    db: CurrentSessionTransaction,
    request_body: MessageHubSendRequest,
) -> MessageHubSendResponse:
    return await hasn_message_hub_service.send(db, request_body)


@router.post(
    '/inbox/pull',
    summary='Pull owner inbox, owned Agent visible copies, and suppressed inbox entries',
    dependencies=[DependsJwtAuth],
)
async def pull_inbox(
    db: CurrentSession,
    request_body: InboxPullRequest,
) -> InboxPullResponse:
    return await hasn_message_hub_service.pull_inbox(db, request_body)
