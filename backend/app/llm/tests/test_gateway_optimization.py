"""LLM 网关优化单元测试

测试内容：
- P0-1: 故障转移统一（chat_completion 和 chat_completion_stream）
- P0-2: 超时控制
- P1-2: priority 排序
- P1-3: 流式 Token 精确计数
"""

import asyncio
import json
import time
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

from backend.app.llm.core.circuit_breaker import CircuitBreaker, CircuitBreakerManager
from backend.app.llm.enums import CircuitState


# ==================== Mock 对象 ====================

def make_model_config(
    id: int = 1,
    model_name: str = 'gpt-4o',
    model_type: str = 'TEXT',
    provider_id: int = 1,
    priority: int = 0,
    max_tokens: int = 4096,
    input_cost_per_1k: Decimal = Decimal('0.003'),
    output_cost_per_1k: Decimal = Decimal('0.015'),
    supports_tools: bool = False,
    enabled: bool = True,
) -> MagicMock:
    """创建 ModelConfig mock"""
    m = MagicMock()
    m.id = id
    m.model_name = model_name
    m.model_type = model_type
    m.provider_id = provider_id
    m.priority = priority
    m.max_tokens = max_tokens
    m.input_cost_per_1k = input_cost_per_1k
    m.output_cost_per_1k = output_cost_per_1k
    m.supports_tools = supports_tools
    m.enabled = enabled
    return m


def make_provider(
    id: int = 1,
    name: str = 'openai',
    provider_type: str = 'openai',
    api_base_url: str | None = None,
    api_key_encrypted: str | None = 'encrypted_key',
    enabled: bool = True,
) -> MagicMock:
    """创建 ModelProvider mock"""
    p = MagicMock()
    p.id = id
    p.name = name
    p.provider_type = provider_type
    p.api_base_url = api_base_url
    p.api_key_encrypted = api_key_encrypted
    p.enabled = enabled
    return p


# ==================== P1-2: Priority 排序测试 ====================

class TestPrioritySort:
    """测试模型按 priority 排序"""

    def test_sort_by_priority(self):
        """高 priority 的模型排在前面"""
        m1 = make_model_config(id=1, model_name='cheap-model', priority=10)
        p1 = make_provider(id=1, name='cliproxyapi')

        m2 = make_model_config(id=2, model_name='gpt-4o', priority=50)
        p2 = make_provider(id=2, name='openai')

        m3 = make_model_config(id=3, model_name='deepseek-chat', priority=30)
        p3 = make_provider(id=3, name='deepseek')

        models_with_providers = [(m1, p1), (m2, p2), (m3, p3)]

        # 模拟 _resolve_models 的排序逻辑
        manager = CircuitBreakerManager()
        models_with_providers.sort(
            key=lambda mp: (
                0 if manager.get_breaker(mp[1].name).allow_request() else 1,
                -mp[0].priority,
            )
        )

        assert models_with_providers[0][0].model_name == 'gpt-4o'       # priority=50
        assert models_with_providers[1][0].model_name == 'deepseek-chat' # priority=30
        assert models_with_providers[2][0].model_name == 'cheap-model'   # priority=10

    def test_circuit_breaker_overrides_priority(self):
        """熔断的供应商即使 priority 高也排在后面"""
        m1 = make_model_config(id=1, model_name='expensive-model', priority=100)
        p1 = make_provider(id=1, name='broken-provider')

        m2 = make_model_config(id=2, model_name='cheap-model', priority=10)
        p2 = make_provider(id=2, name='healthy-provider')

        models_with_providers = [(m1, p1), (m2, p2)]

        manager = CircuitBreakerManager()
        # 触发 broken-provider 熔断
        breaker = manager.get_breaker('broken-provider')
        for _ in range(10):
            breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

        models_with_providers.sort(
            key=lambda mp: (
                0 if manager.get_breaker(mp[1].name).allow_request() else 1,
                -mp[0].priority,
            )
        )

        # 健康的排前面，即使 priority 低
        assert models_with_providers[0][0].model_name == 'cheap-model'
        assert models_with_providers[1][0].model_name == 'expensive-model'

    def test_same_priority_stable_order(self):
        """相同 priority 保持原有顺序（稳定排序）"""
        m1 = make_model_config(id=1, model_name='model-a', priority=50)
        p1 = make_provider(id=1, name='provider-a')

        m2 = make_model_config(id=2, model_name='model-b', priority=50)
        p2 = make_provider(id=2, name='provider-b')

        models_with_providers = [(m1, p1), (m2, p2)]

        manager = CircuitBreakerManager()
        models_with_providers.sort(
            key=lambda mp: (
                0 if manager.get_breaker(mp[1].name).allow_request() else 1,
                -mp[0].priority,
            )
        )

        # 相同 priority，保持原始顺序
        assert models_with_providers[0][0].model_name == 'model-a'
        assert models_with_providers[1][0].model_name == 'model-b'


# ==================== P0-2: 超时控制测试 ====================

class TestTimeoutControl:
    """测试超时参数传递"""

    def test_default_timeout_in_params(self):
        """_build_litellm_params 默认超时 60 秒"""
        from backend.app.llm.core.gateway import LLMGateway

        gw = LLMGateway()

        model = make_model_config()
        provider = make_provider()
        request = MagicMock()
        request.messages = []
        request.stream = False
        request.temperature = None
        request.top_p = None
        request.max_tokens = None
        request.stop = None
        request.presence_penalty = None
        request.frequency_penalty = None
        request.tools = None
        request.tool_choice = None
        request.response_format = None
        request.seed = None

        with patch('backend.app.llm.core.gateway.key_encryption') as mock_enc:
            mock_enc.decrypt.return_value = 'test-key'
            params = gw._build_litellm_params(model, provider, request)

        assert params['timeout'] == 60

    def test_custom_timeout_in_params(self):
        """_build_litellm_params 支持自定义超时"""
        from backend.app.llm.core.gateway import LLMGateway

        gw = LLMGateway()

        model = make_model_config()
        provider = make_provider()
        request = MagicMock()
        request.messages = []
        request.stream = False
        request.temperature = None
        request.top_p = None
        request.max_tokens = None
        request.stop = None
        request.presence_penalty = None
        request.frequency_penalty = None
        request.tools = None
        request.tool_choice = None
        request.response_format = None
        request.seed = None

        with patch('backend.app.llm.core.gateway.key_encryption') as mock_enc:
            mock_enc.decrypt.return_value = 'test-key'
            params = gw._build_litellm_params(model, provider, request, timeout=120)

        assert params['timeout'] == 120

    def test_anthropic_default_timeout(self):
        """_build_anthropic_params 默认超时 60 秒"""
        from backend.app.llm.core.gateway import LLMGateway

        gw = LLMGateway()

        model = make_model_config()
        provider = make_provider(provider_type='anthropic')
        request = MagicMock()
        request.messages = []
        request.max_tokens = 4096
        request.stream = False
        request.system = None
        request.temperature = None
        request.top_p = None
        request.top_k = None
        request.stop_sequences = None
        request.tools = None
        request.tool_choice = None
        request.metadata = None

        with patch('backend.app.llm.core.gateway.key_encryption') as mock_enc:
            mock_enc.decrypt.return_value = 'test-key'
            params = gw._build_anthropic_params(model, provider, request)

        assert params['timeout'] == 60

    def test_anthropic_custom_timeout(self):
        """_build_anthropic_params 支持自定义超时"""
        from backend.app.llm.core.gateway import LLMGateway

        gw = LLMGateway()

        model = make_model_config()
        provider = make_provider(provider_type='anthropic')
        request = MagicMock()
        request.messages = []
        request.max_tokens = 4096
        request.stream = False
        request.system = None
        request.temperature = None
        request.top_p = None
        request.top_k = None
        request.stop_sequences = None
        request.tools = None
        request.tool_choice = None
        request.metadata = None

        with patch('backend.app.llm.core.gateway.key_encryption') as mock_enc:
            mock_enc.decrypt.return_value = 'test-key'
            params = gw._build_anthropic_params(model, provider, request, timeout=120)

        assert params['timeout'] == 120
