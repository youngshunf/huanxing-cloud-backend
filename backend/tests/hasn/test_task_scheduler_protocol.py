from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.app.hasn.api.v1.agent import hasn_task_run as agent_task_run_api
from backend.app.hasn.service import task_scheduler as task_scheduler_module
from backend.app.hasn.service.task_scheduler import TaskSchedulerService
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import get_db, get_db_transaction


class FakeSession:
    def __init__(self, execute_results: list[Any] | None = None) -> None:
        self.added: list[Any] = []
        self.next_id = 456
        self.execute_results = execute_results or []
        self.committed = False

    def add(self, value: Any) -> None:
        self.added.append(value)

    async def flush(self) -> None:
        self.added[-1].id = self.next_id

    async def execute(self, _stmt: object) -> Any:
        return self.execute_results.pop(0)

    async def commit(self) -> None:
        self.committed = True


class FakeResult:
    def __init__(self, value: Any) -> None:
        self.value = value

    def scalar_one_or_none(self) -> Any:
        return self.value


class FakeWsRouter:
    def __init__(self) -> None:
        self.pushed: list[tuple[str, dict[str, Any]]] = []

    async def push_message_to(self, agent_id: str, message: dict[str, Any]) -> bool:
        self.pushed.append((agent_id, message))
        return True


class FakeDbSession:
    def __init__(self, execute_results: list[Any] | None = None) -> None:
        self.execute_results = execute_results or []
        self.committed = False

    async def execute(self, _stmt: object) -> Any:
        return self.execute_results.pop(0)

    async def commit(self) -> None:
        self.committed = True


@pytest.fixture
def agent_api_app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    app = FastAPI()
    app.include_router(agent_task_run_api.router, prefix='/api/v1/hasn/agent/hasn/task/runs')

    async def fake_agent_auth(request: Request):
        request.state.agent = SimpleNamespace(agent_hasn_id='a_agent')
        return None

    async def fake_db() -> FakeDbSession:
        return FakeDbSession()

    app.dependency_overrides[DependsAgentJwtAuth.dependency] = fake_agent_auth
    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_db_transaction] = fake_db
    return app


@pytest.mark.asyncio
async def test_scheduler_dispatch_persists_and_sends_task_session_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.app.hasn.service import task_scheduler as module

    router = FakeWsRouter()
    monkeypatch.setattr(module, 'ws_router', router)

    scheduler = module.TaskSchedulerService()
    session = FakeSession()
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)
    task = SimpleNamespace(
        id=123,
        owner_id='h_owner',
        agent_id='a_agent',
        prompt='生成日报',
        skill_bundle_ids=['backend-dev'],
        skill_ids=['test-driven-development'],
        enabled_toolsets=['terminal'],
        context_from_task_id=None,
        schedule_type='once',
        schedule_config={'run_at': now.isoformat()},
        next_run_at=now,
        last_run_at=None,
        run_count=0,
        repeat_times=None,
        repeat_completed=0,
        enabled=True,
        state='scheduled',
    )

    await scheduler._dispatch_task(session, task, now)

    assert len(session.added) == 1
    task_run = session.added[0]
    assert task_run.session_id == 'sess_task_456'
    assert task_run.source_conversation_id is None
    assert task_run.source_message_id is None
    assert task_run.status == 'pending'

    assert router.pushed == [
        (
            'a_agent',
            {
                'hasn': 'hasn/0.2',
                'method': 'hasn.task.exec',
                'params': {
                    'type': 'task_exec',
                    'task_id': 123,
                    'run_id': 456,
                    'session_id': 'sess_task_456',
                    'source_conversation_id': None,
                    'source_message_id': None,
                    'agent_id': 'a_agent',
                    'prompt': '生成日报',
                    'skill_bundles': ['backend-dev'],
                    'skills': ['test-driven-development'],
                    'enabled_toolsets': ['terminal'],
                    'context': {},
                },
            },
        )
    ]


@pytest.mark.asyncio
async def test_task_result_update_requires_matching_agent() -> None:
    from backend.app.hasn.service import task_scheduler as module
    from backend.common.exception import errors

    scheduler = module.TaskSchedulerService()
    task_run = SimpleNamespace(id=456, task_id=123, agent_id='a_agent', status='pending')
    session = FakeSession(execute_results=[FakeResult(task_run)])

    with pytest.raises(errors.ForbiddenError):
        await scheduler._handle_task_result_in_session(
            session=session,
            run_id=456,
            reporting_agent_id='a_other',
            status='success',
            output='wrong agent',
        )

    assert task_run.status != 'success'
    assert not session.committed


@pytest.mark.asyncio
async def test_task_result_update_persists_matching_agent_result() -> None:
    from backend.app.hasn.service import task_scheduler as module

    scheduler = module.TaskSchedulerService()
    task_run = SimpleNamespace(id=456, task_id=123, agent_id='a_agent', status='pending')
    task = SimpleNamespace(id=123, last_status=None, last_error=None)
    session = FakeSession(execute_results=[FakeResult(task_run), FakeResult(task)])

    success = await scheduler._handle_task_result_in_session(
        session=session,
        run_id=456,
        reporting_agent_id='a_agent',
        prompt_snapshot='Skill bundles: backend-dev\n\n生成日报',
        status='success',
        output='done',
        model='runtime-model',
        token_usage={'input_tokens': 1, 'output_tokens': 2, 'total_tokens': 3},
        duration_ms=1200,
    )

    assert success is True
    assert session.committed is True
    assert task_run.status == 'success'
    assert task_run.output == 'done'
    assert task_run.prompt_snapshot == 'Skill bundles: backend-dev\n\n生成日报'
    assert task_run.model == 'runtime-model'
    assert task_run.duration_ms == 1200
    assert task.last_status == 'success'
    assert task.last_error is None


def test_task_result_route_accepts_only_executing_agent(
    agent_api_app: FastAPI, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_run = SimpleNamespace(id=456, task_id=123, agent_id='a_agent', status='pending')
    task = SimpleNamespace(id=123, last_status=None, last_error=None)
    session = FakeDbSession(execute_results=[FakeResult(task_run), FakeResult(task)])
    monkeypatch.setattr(task_scheduler_module, 'async_db_session', lambda: _session_ctx(session))

    app = agent_api_app
    with TestClient(app) as client:
        response = client.post(
            '/api/v1/hasn/agent/hasn/task/runs/task-result',
            json={
                'run_id': 456,
                'status': 'success',
                'prompt_snapshot': 'Skill bundles: backend-dev\n\n生成日报',
                'output': 'done',
            },
        )

    assert response.status_code == 200, response.text
    assert response.json()['data'] == {'run_id': 456, 'status': 'success'}
    assert task_run.status == 'success'
    assert task_run.output == 'done'
    assert task_run.prompt_snapshot == 'Skill bundles: backend-dev\n\n生成日报'
    assert task.last_status == 'success'
    assert task.last_error is None
    assert session.committed is True


def _session_ctx(session: Any):
    class _Ctx:
        async def __aenter__(self) -> Any:
            return session

        async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
            return None

    return _Ctx()
