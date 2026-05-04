"""单测：HermesRuntimeClient 新加的 4 个 template/credential endpoint
+ chat_completions_stream 流式 SSE 透传（M1 §5.1）。
"""
from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from backend.app.hermes.service.hermes_runtime_client import (
    HermesRuntimeClient,
    HermesRuntimeError,
)


def _make_client() -> HermesRuntimeClient:
    return HermesRuntimeClient(base_url='http://runtime.test', api_token='runtime-test-token', timeout_seconds=2.0)


def _patch_transport(monkeypatch, handler):
    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient

    def patched(*args, **kwargs):
        kwargs['transport'] = transport
        return orig(*args, **kwargs)

    monkeypatch.setattr(httpx, 'AsyncClient', patched)


@pytest.mark.asyncio
async def test_apply_template_posts_correct_url_and_payload(monkeypatch):
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured['method'] = request.method
        captured['url'] = str(request.url)
        captured['body'] = json.loads(request.content)
        captured['auth'] = request.headers.get('Authorization')
        captured['trace'] = request.headers.get('X-Huanxing-Request-Id')
        return httpx.Response(200, json={'status': 'rendered', 'template_version': 'v1.2.0'})

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    payload = {
        'template_id': 'pet-sitter',
        'template_version': 'v1.0.0',
        'package_url': 'https://cdn.example.com/pet-sitter-v1.0.0.tar.gz',
        'file_hash': 'sha256:abc',
        'render_context': {'agent_name': '福仔'},
    }
    result = await client.apply_template('rtp_xyz', payload, trace_id='trace-1')

    assert captured['method'] == 'POST'
    assert captured['url'].endswith('/runtime/v1/agents/rtp_xyz/template/apply')
    assert captured['body'] == payload
    assert captured['auth'] == 'Bearer runtime-test-token'
    assert captured['trace'] == 'trace-1'
    assert result == {'status': 'rendered', 'template_version': 'v1.2.0'}


@pytest.mark.asyncio
async def test_get_template_status_routes_to_status_endpoint(monkeypatch):
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured['method'] = request.method
        captured['url'] = str(request.url)
        return httpx.Response(200, json={'status': 'ready', 'template_id': 'pet-sitter'})

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    result = await client.get_template_status('rtp_xyz', trace_id='trace-2')

    assert captured['method'] == 'GET'
    assert captured['url'].endswith('/runtime/v1/agents/rtp_xyz/template/status')
    assert result == {'status': 'ready', 'template_id': 'pet-sitter'}


@pytest.mark.asyncio
async def test_install_credential_posts_payload(monkeypatch):
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured['method'] = request.method
        captured['url'] = str(request.url)
        captured['body'] = json.loads(request.content)
        return httpx.Response(200, json={'installed': True})

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    payload = {
        'token_key': 'sk-hxTESTONLY1234',
        'base_url': 'https://api.huanxing.ai/api/v1/llm/proxy/v1',
        'default_model': 'openai/gpt-5.5',
    }
    result = await client.install_credential('rtp_xyz', payload, trace_id='trace-3')

    assert captured['method'] == 'POST'
    assert captured['url'].endswith('/runtime/v1/agents/rtp_xyz/credential/install')
    assert captured['body'] == payload
    assert result == {'installed': True}


@pytest.mark.asyncio
async def test_uninstall_credential_deletes(monkeypatch):
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured['method'] = request.method
        captured['url'] = str(request.url)
        return httpx.Response(200, json={'removed': True})

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    result = await client.uninstall_credential('rtp_xyz', trace_id='trace-4')

    assert captured['method'] == 'DELETE'
    assert captured['url'].endswith('/runtime/v1/agents/rtp_xyz/credential')
    assert result == {'removed': True}


@pytest.mark.asyncio
async def test_apply_template_5xx_raises_runtime_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={'error': 'runtime_busy', 'details': 'sandbox queue full'})

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    with pytest.raises(HermesRuntimeError) as exc_info:
        await client.apply_template('rtp_xyz', {'template_id': 'x'}, trace_id='trace-5xx')
    assert exc_info.value.error == 'runtime_busy'
    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_chat_completions_stream_yields_chunks(monkeypatch):
    chunks_to_send = (
        b'data: {"id":"c1","choices":[{"delta":{"content":"He"}}]}\n\n'
        b'data: {"id":"c1","choices":[{"delta":{"content":"llo"}}]}\n\n'
        b'data: [DONE]\n\n'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body.get('stream') is True
        return httpx.Response(
            200,
            headers={'content-type': 'text/event-stream'},
            stream=httpx.ByteStream(chunks_to_send),
        )

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    received: list[bytes] = []
    async for chunk in client.chat_completions_stream(
        'rtp_xyz',
        {'messages': [{'role': 'user', 'content': 'hi'}]},
        trace_id='trace-stream',
    ):
        received.append(chunk)

    assert received
    combined = b''.join(received)
    assert b'He' in combined and b'llo' in combined
    assert b'[DONE]' in combined


@pytest.mark.asyncio
async def test_chat_completions_stream_emits_sse_error_on_4xx(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={'error': 'rate_limited'})

    _patch_transport(monkeypatch, handler)

    client = _make_client()
    received: list[bytes] = []
    async for chunk in client.chat_completions_stream('rtp_xyz', {'messages': []}):
        received.append(chunk)

    combined = b''.join(received)
    assert combined.startswith(b'event: error\n')
    assert b'rate_limited' in combined


@pytest.mark.asyncio
async def test_chat_completions_stream_emits_sse_error_when_base_url_missing():
    client = HermesRuntimeClient(base_url='', api_token='', timeout_seconds=1.0)
    received: list[bytes] = []
    async for chunk in client.chat_completions_stream('rtp_xyz', {'messages': []}):
        received.append(chunk)
    combined = b''.join(received)
    assert combined.startswith(b'event: error\n')
    assert b'runtime_unavailable' in combined
