"""单测：GET /api/v1/hermes/app/templates 列表 endpoint（M1 §5.4）。

策略：搭最小 FastAPI app 挂 router；通过 dependency_overrides 替换 get_db 与 JWT；
mock CurrentSession 的 db.execute 返回伪造 mappings 行；不真连 PostgreSQL。
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.hermes.api.v1.app import templates as templates_module
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import get_db


class _FakeMappingsResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def all(self) -> list[dict[str, Any]]:
        return list(self._rows)

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _FakeExecuteResult:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeMappingsResult:
        return _FakeMappingsResult(self._rows)


class _FakeDB:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.last_stmt: Any = None

    async def execute(self, stmt: Any) -> _FakeExecuteResult:
        self.last_stmt = stmt
        return _FakeExecuteResult(self.rows)


def _build_app(rows: list[dict[str, Any]]) -> tuple[FastAPI, _FakeDB]:
    fake_db = _FakeDB(rows)

    async def _override_db():
        yield fake_db

    async def _override_jwt():
        return SimpleNamespace(id=1001, username='tester')

    app = FastAPI()
    app.include_router(templates_module.router, prefix='/api/v1/hermes/app/templates')
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[DependsJwtAuth.dependency] = _override_jwt
    return app, fake_db


def test_list_templates_returns_filtered_payload_excluding_secrets():
    rows = [
        {
            'app_id': 'pet-sitter',
            'name': '宠物管家',
            'description': '帮你照顾家里的宠物',
            'emoji': '🐾',
            'icon_url': 'https://cdn.example.com/pet-sitter.png',
            'version': 'v1.2.0',
        },
        {
            'app_id': 'media-creator',
            'name': '内容创作',
            'description': None,
            'emoji': '🎬',
            'icon_url': None,
            'version': 'v0.5.0',
        },
    ]
    app, _fake = _build_app(rows)

    with TestClient(app) as client:
        resp = client.get('/api/v1/hermes/app/templates')

    assert resp.status_code == 200, resp.text
    body = resp.json()
    data = body.get('data')
    assert isinstance(data, list)
    assert len(data) == 2

    expected = {'app_id', 'name', 'description', 'emoji', 'icon_url', 'version'}
    assert set(data[0].keys()) == expected
    assert data[0]['app_id'] == 'pet-sitter'
    assert data[0]['version'] == 'v1.2.0'

    forbidden = {'package_url', 'file_hash', 'skill_dependencies', 'app_type'}
    for item in data:
        assert forbidden.isdisjoint(item.keys())


def test_list_templates_returns_empty_array_when_marketplace_has_no_templates():
    app, _fake = _build_app([])

    with TestClient(app) as client:
        resp = client.get('/api/v1/hermes/app/templates')

    assert resp.status_code == 200, resp.text
    data = resp.json().get('data')
    assert data == []
