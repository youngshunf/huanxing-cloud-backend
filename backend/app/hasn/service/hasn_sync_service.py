"""P0 HASN sync/runtime report service.

The service owns the hand-written hasn-node API boundary. Generated CRUD remains
available for admin inspection, but hasn-node uses these redacted, owner-scoped
methods instead of generic table CRUD.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.model import HasnHumans
from backend.app.hasn.schema.hasn_message_hub import ErrorObject
from backend.app.hasn.schema.hasn_sync import (
    ClientEvent,
    RuntimeReportRequest,
    RuntimeReportResponse,
    RuntimeSummary,
    SyncEventRecord,
    SyncPullRequest,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
)
from backend.common.exception import errors
from backend.utils.timezone import timezone

PRIVATE_RUNTIME_KEYS = {
    'workspace',
    'workspace_path',
    'endpoint',
    'local_endpoint',
    'pid',
    'process_id',
    'cli_args',
    'oauth_path',
    'session_cache',
    'token',
    'access_token',
    'refresh_token',
    'raw_binding_metadata',
}

_PRIVATE_METADATA_ERROR = ErrorObject(
    code=8034,
    name='ERR_RUNTIME_PRIVATE_METADATA_REJECTED',
    message='Runtime report contains private local metadata.',
)


class SyncGateway(Protocol):
    async def save_runtime_report(self, db: AsyncSession, report: dict[str, Any]) -> None: ...
    async def pull_events(
        self, db: AsyncSession, *, owner_id: str, after_revision: int, limit: int
    ) -> list[SyncEventRecord]: ...
    async def owns_owner(self, db: AsyncSession, *, owner_id: str, user_id: int) -> bool: ...
    async def save_session(self, db: AsyncSession, session: dict[str, Any]) -> None: ...
    async def save_session_event(self, db: AsyncSession, event: dict[str, Any]) -> None: ...
    async def save_session_artifact(self, db: AsyncSession, artifact: dict[str, Any]) -> None: ...


class SqlAlchemySyncGateway:
    async def owns_owner(self, db: AsyncSession, *, owner_id: str, user_id: int) -> bool:
        result = await db.execute(
            sa.select(HasnHumans.id)
            .where(
                HasnHumans.hasn_id == owner_id,
                HasnHumans.user_id == user_id,
                HasnHumans.status == 'active',
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def save_runtime_report(self, db: AsyncSession, report: dict[str, Any]) -> None:
        summary_json = json.dumps(report['summary_json'], ensure_ascii=False, sort_keys=True, default=str)
        await db.execute(
            sa.text(
                '''
                INSERT INTO public.hasn_agent_runtime_reports (
                    report_id,
                    owner_id,
                    agent_hasn_id,
                    node_id,
                    runtime_type,
                    runtime_status,
                    adapter_registered,
                    handle_available,
                    binding_id,
                    runtime_revision,
                    summary_json,
                    last_seen_at,
                    reported_at,
                    created_time,
                    updated_time
                ) VALUES (
                    :report_id,
                    :owner_id,
                    :agent_hasn_id,
                    :node_id,
                    :runtime_type,
                    :runtime_status,
                    :adapter_registered,
                    :handle_available,
                    :binding_id,
                    :runtime_revision,
                    CAST(:summary_json AS jsonb),
                    :last_seen_at,
                    :reported_at,
                    now(),
                    now()
                )
                ON CONFLICT (report_id) DO UPDATE SET
                    runtime_status = EXCLUDED.runtime_status,
                    adapter_registered = EXCLUDED.adapter_registered,
                    handle_available = EXCLUDED.handle_available,
                    binding_id = EXCLUDED.binding_id,
                    runtime_revision = EXCLUDED.runtime_revision,
                    summary_json = EXCLUDED.summary_json,
                    last_seen_at = EXCLUDED.last_seen_at,
                    reported_at = EXCLUDED.reported_at,
                    updated_time = now()
                '''
            ),
            {**report, 'summary_json': summary_json},
        )
        await self._append_sync_event(
            db,
            owner_id=report['owner_id'],
            hasn_id=report['agent_hasn_id'],
            event_type='runtime.reported',
            aggregate_type='runtime',
            aggregate_id=report['agent_hasn_id'],
            payload={
                'agent_id': report['agent_hasn_id'],
                'node_id': report['node_id'],
                'runtime_type': report['runtime_type'],
                'runtime_status': report['runtime_status'],
                'binding_id': report['binding_id'],
            },
        )

    async def pull_events(
        self, db: AsyncSession, *, owner_id: str, after_revision: int, limit: int
    ) -> list[SyncEventRecord]:
        result = await db.execute(
            sa.text(
                '''
                SELECT event_id, event_type, revision, occurred_at, payload
                FROM public.hasn_sync_events
                WHERE owner_id = :owner_id
                  AND revision > :after_revision
                ORDER BY revision ASC
                LIMIT :limit
                '''
            ),
            {'owner_id': owner_id, 'after_revision': after_revision, 'limit': limit},
        )
        return [
            SyncEventRecord(
                event_id=row['event_id'],
                event_type=row['event_type'],
                revision=int(row['revision']),
                created_at=_coerce_datetime(row['occurred_at']),
                payload=_coerce_dict(row['payload']),
            )
            for row in result.mappings().all()
        ]

    async def save_client_event(
        self, db: AsyncSession, *, owner_id: str, node_id: str, event: ClientEvent
    ) -> None:
        await db.execute(
            sa.text(
                '''
                INSERT INTO public.hasn_sync_inbox_events (
                    client_event_id,
                    owner_id,
                    hasn_id,
                    node_id,
                    event_type,
                    payload,
                    dedupe_key,
                    status,
                    received_at,
                    created_time,
                    updated_time
                ) VALUES (
                    :client_event_id,
                    :owner_id,
                    :hasn_id,
                    :node_id,
                    :event_type,
                    CAST(:payload AS jsonb),
                    :dedupe_key,
                    'accepted',
                    now(),
                    now(),
                    now()
                )
                ON CONFLICT (owner_id, node_id, client_event_id) DO NOTHING
                '''
            ),
            {
                'client_event_id': event.client_event_id,
                'owner_id': owner_id,
                'hasn_id': event.hasn_id or owner_id,
                'node_id': node_id,
                'event_type': event.event_type,
                'payload': json.dumps(event.payload, ensure_ascii=False, sort_keys=True, default=str),
                'dedupe_key': event.dedupe_key,
            },
        )

    async def _append_sync_event(
        self,
        db: AsyncSession,
        *,
        owner_id: str,
        hasn_id: str,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any],
    ) -> None:
        revision_result = await db.execute(
            sa.text(
                '''
                SELECT COALESCE(MAX(revision), 0) + 1 AS revision
                FROM public.hasn_sync_events
                WHERE owner_id = :owner_id
                '''
            ),
            {'owner_id': owner_id},
        )
        revision = int(revision_result.mappings().one()['revision'])
        await db.execute(
            sa.text(
                '''
                INSERT INTO public.hasn_sync_events (
                    event_id,
                    owner_id,
                    hasn_id,
                    event_type,
                    aggregate_type,
                    aggregate_id,
                    payload,
                    revision,
                    occurred_at,
                    created_time,
                    updated_time
                ) VALUES (
                    :event_id,
                    :owner_id,
                    :hasn_id,
                    :event_type,
                    :aggregate_type,
                    :aggregate_id,
                    CAST(:payload AS jsonb),
                    :revision,
                    now(),
                    now(),
                    now()
                )
                '''
            ),
            {
                'event_id': f'se_{uuid.uuid4().hex[:24]}',
                'owner_id': owner_id,
                'hasn_id': hasn_id,
                'event_type': event_type,
                'aggregate_type': aggregate_type,
                'aggregate_id': aggregate_id,
                'payload': json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str),
                'revision': revision,
            },
        )

    async def save_session(self, db: AsyncSession, session: dict[str, Any]) -> None:
        """保存或更新 session 到云端投影表"""
        await db.execute(
            sa.text(
                '''
                INSERT INTO public.hasn_sessions (
                    id,
                    conversation_id,
                    session_kind,
                    session_scope,
                    session_status,
                    origin_type,
                    origin_ref,
                    parent_session_id,
                    fork_point_message_id,
                    summary_checkpoint_json,
                    last_message_id,
                    last_message_at,
                    message_count,
                    created_time,
                    updated_time
                ) VALUES (
                    :id,
                    :conversation_id,
                    :session_kind,
                    :session_scope,
                    :session_status,
                    :origin_type,
                    :origin_ref,
                    :parent_session_id,
                    :fork_point_message_id,
                    :summary_checkpoint_json,
                    :last_message_id,
                    :last_message_at,
                    :message_count,
                    now(),
                    now()
                )
                ON CONFLICT (id) DO UPDATE SET
                    session_status = EXCLUDED.session_status,
                    summary_checkpoint_json = EXCLUDED.summary_checkpoint_json,
                    last_message_id = EXCLUDED.last_message_id,
                    last_message_at = EXCLUDED.last_message_at,
                    message_count = EXCLUDED.message_count,
                    updated_time = now()
                '''
            ),
            session,
        )
        # 只有 conversation_visible 和 summary_only 的 session 才发送同步事件
        if session.get('session_scope') in ('conversation_visible', 'summary_only'):
            await self._append_sync_event(
                db,
                owner_id=session.get('owner_id', ''),
                hasn_id=session.get('owner_id', ''),
                event_type='session.updated',
                aggregate_type='session',
                aggregate_id=session['id'],
                payload={
                    'session_id': session['id'],
                    'conversation_id': str(session.get('conversation_id')) if session.get('conversation_id') else None,
                    'session_kind': session.get('session_kind'),
                    'session_status': session.get('session_status'),
                },
            )

    async def save_session_event(self, db: AsyncSession, event: dict[str, Any]) -> None:
        """保存 session event 到云端投影表（仅 summary_only 和 conversation_visible）"""
        await db.execute(
            sa.text(
                '''
                INSERT INTO public.hasn_session_events (
                    session_id,
                    event_type,
                    event_seq,
                    payload_json,
                    occurred_at,
                    created_time
                ) VALUES (
                    :session_id,
                    :event_type,
                    :event_seq,
                    :payload_json,
                    :occurred_at,
                    now()
                )
                '''
            ),
            event,
        )

    async def save_session_artifact(self, db: AsyncSession, artifact: dict[str, Any]) -> None:
        """保存 session artifact 到云端投影表（按 sync_policy 决定）"""
        await db.execute(
            sa.text(
                '''
                INSERT INTO public.hasn_session_artifacts (
                    session_id,
                    artifact_kind,
                    artifact_name,
                    artifact_path,
                    summary_json,
                    sync_policy,
                    created_time
                ) VALUES (
                    :session_id,
                    :artifact_kind,
                    :artifact_name,
                    :artifact_path,
                    :summary_json,
                    :sync_policy,
                    now()
                )
                '''
            ),
            artifact,
        )


@dataclass(slots=True)
class HasnSyncService:
    gateway: SyncGateway = field(default_factory=SqlAlchemySyncGateway)

    async def pull(self, db: AsyncSession, request: SyncPullRequest, *, user_id: int | None = None) -> SyncPullResponse:
        await self._assert_owner_access(db, owner_id=request.owner_id, user_id=user_id)
        after_revision = _parse_owner_cursor(request.cursor)
        events = await self.gateway.pull_events(
            db,
            owner_id=request.owner_id,
            after_revision=after_revision,
            limit=request.limit + 1,
        )
        limited = events[: request.limit]
        has_more = len(events) > request.limit
        next_revision = limited[-1].revision if limited else after_revision
        return SyncPullResponse(
            events=limited,
            next_cursor=_owner_cursor(request.owner_id, next_revision),
            has_more=has_more,
        )

    async def push(self, db: AsyncSession, request: SyncPushRequest, *, user_id: int | None = None) -> SyncPushResponse:
        await self._assert_owner_access(db, owner_id=request.owner_id, user_id=user_id)
        rejected: list[ErrorObject] = []
        node_id = request.node_id or 'unknown'
        for event in request.events:
            if _contains_private_runtime_key(event.payload):
                rejected.append(_PRIVATE_METADATA_ERROR)
                continue

            # 处理 session 相关事件
            if event.event_type == 'session.sync':
                save_session = getattr(self.gateway, 'save_session', None)
                if save_session and event.payload:
                    session_data = dict(event.payload)
                    session_data['owner_id'] = request.owner_id
                    await save_session(db, session_data)
            elif event.event_type == 'session_event.sync':
                save_session_event = getattr(self.gateway, 'save_session_event', None)
                if save_session_event and event.payload:
                    await save_session_event(db, event.payload)
            elif event.event_type == 'session_artifact.sync':
                save_session_artifact = getattr(self.gateway, 'save_session_artifact', None)
                if save_session_artifact and event.payload:
                    await save_session_artifact(db, event.payload)
            else:
                # 其他事件类型使用原有逻辑
                save_client_event = getattr(self.gateway, 'save_client_event', None)
                if save_client_event:
                    await save_client_event(db, owner_id=request.owner_id, node_id=node_id, event=event)
        accepted = len(request.events) - len(rejected)
        return SyncPushResponse(
            accepted=accepted,
            rejected=rejected,
            next_cursor=_owner_cursor(request.owner_id, 0),
        )

    async def report_runtime(
        self, db: AsyncSession, request: RuntimeReportRequest, *, user_id: int | None = None
    ) -> RuntimeReportResponse:
        await self._assert_owner_access(db, owner_id=request.owner_id, user_id=user_id)
        for summary in request.runtime_summaries:
            if _contains_private_runtime_key(summary.summary_json):
                raise errors.RequestError(msg=_PRIVATE_METADATA_ERROR.name, data=_PRIVATE_METADATA_ERROR.model_dump())

        for summary in request.runtime_summaries:
            await self.gateway.save_runtime_report(
                db,
                {
                    'report_id': _report_id(request.owner_id, request.node_id, summary),
                    'owner_id': request.owner_id,
                    'agent_hasn_id': summary.agent_id,
                    'node_id': request.node_id,
                    'runtime_type': summary.runtime_type,
                    'runtime_status': _runtime_status_for_storage(summary.status),
                    'adapter_registered': summary.adapter_registered,
                    'handle_available': summary.handle_available,
                    'binding_id': summary.binding_id,
                    'runtime_revision': summary.runtime_revision,
                    'summary_json': _redact_runtime_summary(summary.summary_json),
                    'last_seen_at': summary.last_seen_at,
                    'reported_at': timezone.now(),
                },
            )
        return RuntimeReportResponse(
            accepted=len(request.runtime_summaries),
            rejected=[],
            next_cursor=_owner_cursor(request.owner_id, 0),
        )

    async def _assert_owner_access(self, db: AsyncSession, *, owner_id: str, user_id: int | None) -> None:
        if user_id is None:
            return
        owns_owner = getattr(self.gateway, 'owns_owner', None)
        if owns_owner is None:
            raise errors.AuthorizationError(msg='ERR_HASN_OWNER_ACCESS_DENIED')
        if not await owns_owner(db, owner_id=owner_id, user_id=user_id):
            raise errors.AuthorizationError(msg='ERR_HASN_OWNER_ACCESS_DENIED')


def _parse_owner_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    parts = str(cursor).rsplit(':', maxsplit=1)
    try:
        return max(int(parts[-1]), 0)
    except (TypeError, ValueError) as exc:
        raise errors.RequestError(msg='ERR_SYNC_CURSOR_INVALID') from exc


def _owner_cursor(owner_id: str, revision: int) -> str:
    return f'owner:{owner_id}:{max(int(revision), 0)}'


def _report_id(owner_id: str, node_id: str, summary: RuntimeSummary) -> str:
    stable = uuid.uuid5(uuid.NAMESPACE_URL, f'hasn:runtime-report:{owner_id}:{node_id}:{summary.agent_id}')
    return f'rr_{stable.hex[:24]}'


def _runtime_status_for_storage(status: str) -> str:
    if status == 'missing':
        return 'unavailable'
    if status == 'failed':
        return 'error'
    return status


def _contains_private_runtime_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in PRIVATE_RUNTIME_KEYS:
                return True
            if _contains_private_runtime_key(child):
                return True
    elif isinstance(value, list):
        return any(_contains_private_runtime_key(item) for item in value)
    return False


def _redact_runtime_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in dict(summary).items()
        if str(key).lower() not in PRIVATE_RUNTIME_KEYS
    }


def _coerce_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return timezone.now()


def _coerce_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


hasn_sync_service = HasnSyncService()
