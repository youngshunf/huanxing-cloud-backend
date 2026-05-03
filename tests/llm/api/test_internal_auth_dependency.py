"""单测：require_runtime_internal_token dependency（§09 §5）。

验证 X-Internal-Token header 校验三种路径：
- 缺 header → 401
- 错 token → 401
- 正确 token → 通过
+ 服务端未配置 RUNTIME_INTERNAL_TOKEN → 401（避免空字符串绕过）
"""
from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.common.security.internal_auth import require_runtime_internal_token


@pytest.fixture
def expected_token() -> str:
    return 'test-runtime-internal-token-XYZ-123'


@pytest.fixture
def test_app(monkeypatch, expected_token):
    """最小 FastAPI app，仅含一个被 require_runtime_internal_token 守护的路由。"""
    from backend.common.security import internal_auth as ia_mod

    # 通过 monkeypatch settings.RUNTIME_INTERNAL_TOKEN（dependency 内部读取）
    monkeypatch.setattr(ia_mod.settings, 'RUNTIME_INTERNAL_TOKEN', expected_token)

    app = FastAPI()

    @app.post('/protected', dependencies=[Depends(require_runtime_internal_token)])
    async def protected():
        return {'ok': True}

    return app


def test_missing_internal_token_returns_401(test_app):
    """缺 X-Internal-Token header → 401"""
    with TestClient(test_app) as client:
        resp = client.post('/protected')
    assert resp.status_code == 401


def test_wrong_internal_token_returns_401(test_app):
    """错误 token → 401"""
    with TestClient(test_app) as client:
        resp = client.post('/protected', headers={'X-Internal-Token': 'WRONG'})
    assert resp.status_code == 401


def test_correct_internal_token_passes(test_app, expected_token):
    """正确 token → 200"""
    with TestClient(test_app) as client:
        resp = client.post('/protected', headers={'X-Internal-Token': expected_token})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {'ok': True}


def test_unconfigured_token_returns_401(monkeypatch):
    """服务端未配置 RUNTIME_INTERNAL_TOKEN（空字符串）→ 401，
    避免攻击者发空 header 绕过"""
    from backend.common.security import internal_auth as ia_mod

    monkeypatch.setattr(ia_mod.settings, 'RUNTIME_INTERNAL_TOKEN', '')

    app = FastAPI()

    @app.post('/protected', dependencies=[Depends(require_runtime_internal_token)])
    async def protected():
        return {'ok': True}

    with TestClient(app) as client:
        # 即使 attacker 发空 header 也不能通过
        resp = client.post('/protected', headers={'X-Internal-Token': ''})
        assert resp.status_code == 401

        # 即使 attacker 发非空 header 也不行
        resp2 = client.post('/protected', headers={'X-Internal-Token': 'anything'})
        assert resp2.status_code == 401
