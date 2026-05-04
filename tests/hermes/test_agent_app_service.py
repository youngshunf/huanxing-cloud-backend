"""单测：HermesAgentAppService.create_agent BYOK fast-fail
+ _resolve_template marketplace 查询（M1 §5.2 sub-tasks a + b）。

风格 mirror backend/tests/hermes/test_agent_app_service.py：使用 SimpleNamespace
+ InMemorySession-style stub，避免真连 PostgreSQL。
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from backend.app.hermes.service.hermes_agent_app_service import HermesAgentAppService
from backend.common.exception import errors


class _MarketplaceAppStub:
    def __init__(self, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


class _MarketplaceAppVersionStub:
    def __init__(self, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


class _MarketplaceSession:
    """Minimal stub session that the service's hasattr-branch picks up."""

    def __init__(self) -> None:
        self.marketplace_apps: list[_MarketplaceAppStub] = []
        self.marketplace_app_versions: list[_MarketplaceAppVersionStub] = []

    async def flush(self) -> None:
        return None

    def add(self, _obj: Any) -> None:
        return None


def _byok_payload() -> SimpleNamespace:
    return SimpleNamespace(
        agent_name='福仔',
        template='pet-sitter',
        timezone='Asia/Shanghai',
        soul=None,
        user_profile=None,
        auto_start_gateway=False,
        llm_mode='byok',
    )


@pytest.mark.asyncio
async def test_create_agent_rejects_byok_mode_with_request_error():
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_byok')
    with pytest.raises(errors.RequestError) as exc_info:
        await service.create_agent(db=_MarketplaceSession(), user_id=1001, payload=_byok_payload())
    assert 'BYOK' in exc_info.value.msg or 'byok' in exc_info.value.msg.lower()
    assert 'platform' in exc_info.value.msg


@pytest.mark.asyncio
async def test_resolve_template_happy_path_returns_version_and_package_metadata():
    db = _MarketplaceSession()
    db.marketplace_apps.append(
        _MarketplaceAppStub(
            app_id='pet-sitter',
            app_type='agent_template',
            name='宠物管家',
            description='帮你照顾家里的宠物',
            emoji='🐾',
            icon_url='https://cdn.example.com/pet-sitter.png',
            skill_dependencies='skill-feed,skill-vet',
        )
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(
            app_id='pet-sitter',
            version='v1.2.0',
            package_url='https://cdn.example.com/pet-sitter-v1.2.0.tar.gz',
            file_hash='sha256:abc123',
            is_latest=True,
            published_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(
            app_id='pet-sitter',
            version='v1.0.0',
            package_url='https://cdn.example.com/pet-sitter-v1.0.0.tar.gz',
            file_hash='sha256:old',
            is_latest=False,
        )
    )

    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    result = await service._resolve_template(db, 'pet-sitter')

    assert result['app_id'] == 'pet-sitter'
    assert result['version'] == 'v1.2.0'
    assert result['package_url'].endswith('pet-sitter-v1.2.0.tar.gz')
    assert result['file_hash'] == 'sha256:abc123'
    assert result['name'] == '宠物管家'
    assert result['emoji'] == '🐾'


@pytest.mark.asyncio
async def test_resolve_template_raises_when_app_missing():
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError) as exc_info:
        await service._resolve_template(_MarketplaceSession(), 'unknown-template')
    assert exc_info.value.msg == 'template_not_found'


@pytest.mark.asyncio
async def test_resolve_template_raises_when_no_latest_version_published():
    db = _MarketplaceSession()
    db.marketplace_apps.append(
        _MarketplaceAppStub(app_id='media-creator', app_type='agent_template', name='Media Creator')
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(
            app_id='media-creator', version='v0.1.0', is_latest=False, package_url='x', file_hash='y'
        )
    )
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError) as exc_info:
        await service._resolve_template(db, 'media-creator')
    assert exc_info.value.msg == 'template_not_found'


@pytest.mark.asyncio
async def test_resolve_template_filters_out_skill_pack_apps():
    """app_type='skill_pack' 不能被当成模板用（即使 app_id 撞名）。"""
    db = _MarketplaceSession()
    db.marketplace_apps.append(
        _MarketplaceAppStub(app_id='skill-imposter', app_type='skill_pack', name='Skill Pack')
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(app_id='skill-imposter', version='v1', is_latest=True, package_url='', file_hash='')
    )
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError):
        await service._resolve_template(db, 'skill-imposter')


@pytest.mark.asyncio
async def test_resolve_template_with_empty_template_id_raises():
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError):
        await service._resolve_template(_MarketplaceSession(), '')
