"""默认 Agent 采用 hub `assistant` 模板：onboarding 创建时把 SOUL/AGENTS/USER + 技能
物化进 hasn_agents（与 WebUI 手动建 assistant 等价）。

测试策略：monkeypatch 两个 marketplace 模板 DAO 读 + register_hasn_agent，捕获 gateway
转发给 register_hasn_agent 的 kwargs，断言模板字段被正确映射；并覆盖「模板缺失回退」
分支。register_hasn_agent 自身的落库/幂等回填在 hasn_auth 层 + 真实 DB 集成验证覆盖。
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from backend.app.hasn.service import hasn_onboarding_service as svc
from backend.app.hasn.service.hasn_onboarding_service import (
    DEFAULT_AGENT_DISPLAY_NAME,
    DEFAULT_AGENT_NAME,
    DEFAULT_AGENT_TEMPLATE_ID,
    SqlAlchemyOnboardingGateway,
)


def _template_stub() -> SimpleNamespace:
    """模拟 marketplace_template 里 huanxing/agent/assistant 行（含正文 + 技能依赖）。"""
    return SimpleNamespace(
        template_id=DEFAULT_AGENT_TEMPLATE_ID,
        name='星诺',
        description='您专属的顶级执行管家',
        soul_md='# SOUL.md — 我是星诺 💎',
        agents_md='# AGENTS.md',
        user_md='# USER.md',
        skill_dependencies='huanxing/utility/weather, huanxing/utility/calculator',
    )


def _capture_register(monkeypatch) -> dict[str, Any]:
    """monkeypatch register_hasn_agent，捕获 kwargs；返回 captured dict。"""
    captured: dict[str, Any] = {}

    async def _fake_register(**kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return {
            'agent': SimpleNamespace(hasn_id='a_default_test'),
            'agent_key': None,
            'already_exists': False,
        }

    monkeypatch.setattr(svc.hasn_auth_service, 'register_hasn_agent', _fake_register, raising=True)
    return captured


@pytest.mark.asyncio
async def test_ensure_default_agent_materializes_assistant_template(monkeypatch) -> None:
    """模板存在 → 把 template_id/soul/agents/user/skills + display_name 映射进 register_hasn_agent。"""
    tpl = _template_stub()

    async def _get_by_id(_db: Any, template_id: str) -> Any:
        assert template_id == DEFAULT_AGENT_TEMPLATE_ID
        return tpl

    async def _get_latest(_db: Any, template_id: str) -> Any:
        assert template_id == DEFAULT_AGENT_TEMPLATE_ID
        return SimpleNamespace(version='2.0.1')

    monkeypatch.setattr(svc.marketplace_template_dao, 'get_by_id', _get_by_id, raising=True)
    monkeypatch.setattr(
        svc.marketplace_template_version_dao, 'get_latest_by_template', _get_latest, raising=True
    )
    captured = _capture_register(monkeypatch)

    gateway = SqlAlchemyOnboardingGateway()
    agent, created = await gateway.ensure_default_agent(db=None, owner_id='h_owner_1', node_id='n_1')

    assert created is True
    assert agent.hasn_id == 'a_default_test'
    # slug 槽位保持 assistant（daemon 镜像依赖 → star_id `<owner>#assistant`）。
    assert captured['agent_name'] == DEFAULT_AGENT_NAME == 'assistant'
    # 人格来自模板，不再是「唤星默认 Agent」空壳。
    assert captured['display_name'] == '星诺'
    assert captured['template_id'] == DEFAULT_AGENT_TEMPLATE_ID
    assert captured['template_version'] == '2.0.1'
    assert captured['soul_md'] == tpl.soul_md
    assert captured['agents_md'] == tpl.agents_md
    assert captured['user_md'] == tpl.user_md
    # 技能装配：逗号分隔 → enabled 列表（去空白）。
    assert captured['skills'] == {
        'enabled': ['huanxing/utility/weather', 'huanxing/utility/calculator']
    }
    # A2A 能力描述符与人格模板正交，保留。
    assert captured['capabilities'] == [svc.DEFAULT_AGENT_TEMPLATE]
    assert captured['role'] == 'primary'
    assert captured['created_via'] == 'onboarding'


@pytest.mark.asyncio
async def test_ensure_default_agent_falls_back_when_template_missing(monkeypatch) -> None:
    """模板缺失（云端尚未 sync）→ 不阻断 onboarding，退回纯身份创建（零 fake）。"""
    async def _get_by_id(_db: Any, _template_id: str) -> Any:
        return None

    monkeypatch.setattr(svc.marketplace_template_dao, 'get_by_id', _get_by_id, raising=True)
    captured = _capture_register(monkeypatch)

    gateway = SqlAlchemyOnboardingGateway()
    agent, created = await gateway.ensure_default_agent(db=None, owner_id='h_owner_2', node_id=None)

    assert created is True
    assert agent.hasn_id == 'a_default_test'
    assert captured['agent_name'] == DEFAULT_AGENT_NAME
    # 模板缺失 → 用兜底 display_name，且不带 persona / 模板字段。
    assert captured['display_name'] == DEFAULT_AGENT_DISPLAY_NAME
    assert captured['template_id'] is None
    assert captured['template_version'] is None
    assert captured['soul_md'] is None
    assert captured['agents_md'] is None
    assert captured['user_md'] is None
    assert captured['skills'] is None
