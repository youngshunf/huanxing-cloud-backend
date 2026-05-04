"""单测：POST /api/v1/hermes/app/agents/{id}/chat/completions SSE 透传（M1 §5.5）。

策略：搭最小 FastAPI app，monkeypatch hermes_agent_app_service 的
stream_chat_completions 直接 yield 伪 chunks；assert content-type 为
text/event-stream 且 body 把 chunks 拼回去；non-stream 路径保持原 dict 行为。
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.hermes.api.v1.app import agents as agents_module
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import get_db_transaction


class _NopDB:
    async def execute(self, *a, **kw):
        return None

    async def flush(self) -> None:
        return None

    def add(self, _obj: Any) -> None:
        return None


def _build_app() -> FastAPI:
    async def _override_db():
        yield _NopDB()

    async def _override_jwt():
        return SimpleNamespace(id=1001, username='tester')

    app = FastAPI()

    # endpoint 通过 request.user.id 取 user，必须在 ASGI scope 里 inject。
    @app.middleware('http')
    async def _inject_fake_user(request, call_next):
        request.scope['user'] = SimpleNamespace(id=1001, username='tester')
        return await call_next(request)

    app.include_router(agents_module.router, prefix='/api/v1/hermes/app/agents')
    app.dependency_overrides[get_db_transaction] = _override_db
    app.dependency_overrides[DependsJwtAuth.dependency] = _override_jwt
    return app


def test_chat_completions_stream_true_returns_text_event_stream(monkeypatch):
    chunks = [
        b'data: {"id":"c1","choices":[{"delta":{"content":"He"}}]}\n\n',
        b'data: {"id":"c1","choices":[{"delta":{"content":"llo"}}]}\n\n',
        b'data: [DONE]\n\n',
    ]

    async def _fake_stream(db, *, user_id, agent_id, payload, trace_id=None):
        for c in chunks:
            yield c

    monkeypatch.setattr(
        agents_module.hermes_agent_app_service, 'stream_chat_completions', _fake_stream
    )

    app = _build_app()
    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/hermes/app/agents/agt_x/chat/completions',
            json={'messages': [{'role': 'user', 'content': 'hi'}], 'stream': True},
        )

    assert resp.status_code == 200, resp.text
    assert resp.headers['content-type'].startswith('text/event-stream')
    body = resp.content
    assert b'He' in body and b'llo' in body
    assert b'[DONE]' in body


def test_chat_completions_stream_false_returns_response_model(monkeypatch):
    """stream 缺失或 False → 走原 ResponseModel 路径，响应是 JSON dict"""

    async def _fake_completions(db, *, user_id, agent_id, payload, trace_id=None):
        return {'id': 'chatcmpl_test', 'choices': [{'message': {'role': 'assistant', 'content': 'ok'}}]}

    monkeypatch.setattr(
        agents_module.hermes_agent_app_service, 'chat_completions', _fake_completions
    )

    app = _build_app()
    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/hermes/app/agents/agt_x/chat/completions',
            json={'messages': [{'role': 'user', 'content': 'hi'}]},
        )

    assert resp.status_code == 200, resp.text
    assert resp.headers['content-type'].startswith('application/json')
    body = resp.json()
    assert body.get('data', {}).get('id') == 'chatcmpl_test'


def test_chat_completions_stream_runtime_error_emits_sse_error_frame(monkeypatch):
    """service.stream_chat_completions 抛 HermesRuntimeError → endpoint
    yield SSE error 帧而非 500"""
    from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError

    async def _failing_stream(db, *, user_id, agent_id, payload, trace_id=None):
        # 让函数真的是 async generator
        if False:
            yield b''
        raise HermesRuntimeError(error='runtime_unavailable', details='down')

    monkeypatch.setattr(
        agents_module.hermes_agent_app_service, 'stream_chat_completions', _failing_stream
    )

    app = _build_app()
    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/hermes/app/agents/agt_x/chat/completions',
            json={'messages': [], 'stream': True},
        )

    assert resp.status_code == 200, resp.text
    assert resp.headers['content-type'].startswith('text/event-stream')
    assert resp.content.startswith(b'event: error\n')
    assert b'runtime_unavailable' in resp.content
