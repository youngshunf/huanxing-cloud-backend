from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette_context.middleware import ContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from backend.app.marketplace.api.v1 import skill_pack as skill_pack_api
from backend.common.exception.exception_handler import register_exception
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import get_db, get_db_transaction


class FakeMappingResult:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = rows or []

    def mappings(self) -> 'FakeMappingResult':
        return self

    def all(self) -> list[dict[str, Any]]:
        return self.rows


class FakeSkillPackDb:
    def __init__(self) -> None:
        self.templates: dict[str, dict[str, Any]] = {}
        self.versions: dict[tuple[str, str], dict[str, Any]] = {}
        self.executed: list[tuple[str, dict[str, Any] | None]] = []

    async def execute(self, stmt: Any, params: dict[str, Any] | None = None) -> FakeMappingResult:
        sql = str(stmt)
        self.executed.append((sql, params))
        if sql.lstrip().upper().startswith('SELECT'):
            return FakeMappingResult(self._list_skill_packs((params or {}).get('user_id')))
        assert params is not None
        if 'INSERT INTO public.marketplace_template (' in sql:
            self.templates[params['template_id']] = {
                'template_id': params['template_id'],
                'name': params['name'],
                'description': params['description'],
                'author_id': params['author_id'],
                'template_type': 'skill_pack',
                'is_private': params['is_private'],
                'is_official': params['is_official'],
                'download_count': 0,
            }
        elif 'UPDATE public.marketplace_template_version' in sql:
            for version in self.versions.values():
                if version['template_id'] == params['template_id']:
                    version['is_latest'] = False
        elif 'INSERT INTO public.marketplace_template_version (' in sql:
            key = (params['template_id'], params['version'])
            self.versions[key] = {
                'template_id': params['template_id'],
                'version': params['version'],
                'bundle_slug': params['bundle_slug'],
                'command_key': params['command_key'],
                'hermes_bundle_json': json.loads(params['hermes_bundle_json']),
                'hermes_yaml': params['hermes_yaml'],
                'content_hash': params['content_hash'],
                'file_hash': params['content_hash'],
                'package_url': None,
                'published_at': None,
                'is_latest': True,
            }
        return FakeMappingResult()

    def _list_skill_packs(self, user_id: int | None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for version in self.versions.values():
            template = self.templates.get(version['template_id'])
            if not template or template['template_type'] != 'skill_pack' or not version['is_latest']:
                continue
            if template['is_private'] and template['author_id'] != user_id and not template['is_official']:
                continue
            rows.append({
                **version,
                'name': template['name'],
                'description': template['description'],
            })
        return rows


def make_app(db: FakeSkillPackDb) -> FastAPI:
    app = FastAPI()
    app.add_middleware(ContextMiddleware, plugins=[RequestIdPlugin(validate=True)])
    register_exception(app)
    app.include_router(skill_pack_api.router, prefix='/api/v1/marketplace/skill-packs')

    async def fake_db():
        yield db

    async def fake_auth(request: Request) -> None:
        request.scope['user'] = SimpleNamespace(id=7)

    async def fake_user_scope(request: Request) -> None:
        request.scope['user'] = SimpleNamespace(id=7)

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_db_transaction] = fake_db
    app.dependency_overrides[DependsJwtAuth.dependency] = fake_auth
    app.middleware('http')(lambda request, call_next: _with_user_scope(request, call_next, fake_user_scope))
    return app


async def _with_user_scope(request: Request, call_next: Any, setter: Any) -> Any:
    await setter(request)
    return await call_next(request)


def test_skill_pack_create_and_list_returns_hermes_contract() -> None:
    db = FakeSkillPackDb()
    client = TestClient(make_app(db))

    create = client.post(
        '/api/v1/marketplace/skill-packs',
        headers={'Authorization': 'Bearer owner.jwt'},
        json={
            'namespace': 'huanxing',
            'name': '后端开发',
            'description': 'Backend tools',
            'bundle_slug': 'backend-dev',
            'command_key': '/backend-dev',
            'version': '1.0.0',
            'hermes_bundle_json': {'skills': ['pytest']},
            'hermes_yaml': 'name: backend-dev\nskills:\n  - pytest\n',
            'content_hash': 'sha256:abc123',
            'is_private': False,
            'is_official': True,
        },
    )
    listed = client.get('/api/v1/marketplace/skill-packs')

    assert create.status_code == 200, create.text
    assert create.json()['data']['template_id'] == 'huanxing/backend-dev'
    assert create.json()['data']['bundle_slug'] == 'backend-dev'
    assert create.json()['data']['content_hash'] == 'sha256:abc123'
    assert listed.status_code == 200, listed.text
    assert listed.json()['data'][0]['command_key'] == '/backend-dev'
    assert listed.json()['data'][0]['hermes_yaml'].startswith('name: backend-dev')
    assert listed.json()['data'][0]['hermes_bundle_json'] == {'skills': ['pytest']}


def test_skill_pack_list_includes_current_user_private_packs() -> None:
    db = FakeSkillPackDb()
    client = TestClient(make_app(db))

    create = client.post(
        '/api/v1/marketplace/skill-packs',
        headers={'Authorization': 'Bearer owner.jwt'},
        json={
            'namespace': 'huanxing',
            'name': '我的私有技能包',
            'bundle_slug': 'my-private-pack',
            'command_key': '/my-private-pack',
            'version': '1.0.0',
            'hermes_bundle_json': {'skills': ['private-skill']},
            'hermes_yaml': 'name: my-private-pack\nskills:\n  - private-skill\n',
            'content_hash': 'sha256:private123',
            'is_private': True,
            'is_official': False,
        },
    )
    listed = client.get('/api/v1/marketplace/skill-packs', headers={'Authorization': 'Bearer owner.jwt'})

    assert create.status_code == 200, create.text
    assert listed.status_code == 200, listed.text
    assert [item['bundle_slug'] for item in listed.json()['data']] == ['my-private-pack']
    select_sql, select_params = db.executed[-1]
    assert 't.author_id = :user_id' in select_sql
    assert select_params == {'user_id': 7}
