"""熔断器单元测试

测试内容：
- P1-1: 熔断器参数调整（阈值 10，恢复 60s，半开 5 次）
- 基本状态转换逻辑
"""

import time
from unittest.mock import patch

import pytest

from backend.app.llm.core.circuit_breaker import CircuitBreaker, CircuitBreakerManager
from backend.app.llm.enums import CircuitState


class TestCircuitBreakerDefaults:
    """P1-1: 测试熔断器默认参数"""

    def test_default_failure_threshold(self):
        """默认失败阈值应为 10"""
        breaker = CircuitBreaker('test')
        assert breaker.failure_threshold == 10

    def test_default_recovery_timeout(self):
        """默认恢复超时应为 60 秒"""
        breaker = CircuitBreaker('test')
        assert breaker.recovery_timeout == 60

    def test_default_half_open_max_calls(self):
        """默认半开最大调用应为 5"""
        breaker = CircuitBreaker('test')
        assert breaker.half_open_max_calls == 5

    def test_custom_params(self):
        """支持自定义参数"""
        breaker = CircuitBreaker('test', failure_threshold=3, recovery_timeout=15, half_open_max_calls=2)
        assert breaker.failure_threshold == 3
        assert breaker.recovery_timeout == 15
        assert breaker.half_open_max_calls == 2


class TestCircuitBreakerStateTransitions:
    """测试熔断器状态转换"""

    def test_initial_state_is_closed(self):
        """初始状态应为 CLOSED"""
        breaker = CircuitBreaker('test')
        assert breaker.state == CircuitState.CLOSED

    def test_closed_allows_requests(self):
        """CLOSED 状态允许请求"""
        breaker = CircuitBreaker('test')
        assert breaker.allow_request() is True

    def test_stays_closed_under_threshold(self):
        """失败次数未达阈值时保持 CLOSED"""
        breaker = CircuitBreaker('test', failure_threshold=10)
        for _ in range(9):
            breaker.record_failure()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.allow_request() is True

    def test_opens_at_threshold(self):
        """失败次数达到阈值时转为 OPEN"""
        breaker = CircuitBreaker('test', failure_threshold=10)
        for _ in range(10):
            breaker.record_failure()
        assert breaker.state == CircuitState.OPEN
        assert breaker.allow_request() is False

    def test_open_to_half_open_after_timeout(self):
        """OPEN 状态超过恢复超时后转为 HALF_OPEN"""
        breaker = CircuitBreaker('test', failure_threshold=3, recovery_timeout=1)
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

        time.sleep(1.1)
        assert breaker.state == CircuitState.HALF_OPEN
        assert breaker.allow_request() is True

    def test_half_open_limits_calls(self):
        """HALF_OPEN 状态限制调用次数"""
        breaker = CircuitBreaker('test', failure_threshold=3, recovery_timeout=1, half_open_max_calls=5)
        for _ in range(3):
            breaker.record_failure()

        time.sleep(1.1)
        # 应允许 5 次调用
        for _ in range(5):
            assert breaker.allow_request() is True
        # 第 6 次应拒绝
        assert breaker.allow_request() is False

    def test_half_open_to_closed_on_success(self):
        """HALF_OPEN 状态下足够多成功后转为 CLOSED"""
        breaker = CircuitBreaker('test', failure_threshold=3, recovery_timeout=1, half_open_max_calls=5)
        for _ in range(3):
            breaker.record_failure()

        time.sleep(1.1)
        # 模拟 5 次成功
        for _ in range(5):
            breaker.allow_request()
            breaker.record_success()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_half_open_to_open_on_failure(self):
        """HALF_OPEN 状态下失败立即回到 OPEN"""
        breaker = CircuitBreaker('test', failure_threshold=3, recovery_timeout=1)
        for _ in range(3):
            breaker.record_failure()

        time.sleep(1.1)
        assert breaker.state == CircuitState.HALF_OPEN

        breaker.allow_request()
        breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

    def test_success_resets_failure_count(self):
        """CLOSED 状态下成功重置失败计数"""
        breaker = CircuitBreaker('test', failure_threshold=10)
        for _ in range(8):
            breaker.record_failure()
        assert breaker.failure_count == 8

        breaker.record_success()
        assert breaker.failure_count == 0

    def test_reset(self):
        """reset 重置所有状态"""
        breaker = CircuitBreaker('test', failure_threshold=3)
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state == CircuitState.OPEN

        breaker.reset()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_get_status(self):
        """get_status 返回正确信息"""
        breaker = CircuitBreaker('test-provider', failure_threshold=10, recovery_timeout=60)
        status = breaker.get_status()
        assert status['name'] == 'test-provider'
        assert status['state'] == 'CLOSED'
        assert status['failure_threshold'] == 10
        assert status['recovery_timeout'] == 60


class TestCircuitBreakerManager:
    """测试熔断器管理器"""

    def test_get_or_create(self):
        """获取不存在的熔断器时自动创建"""
        manager = CircuitBreakerManager()
        breaker = manager.get_breaker('new-provider')
        assert breaker.name == 'new-provider'

    def test_get_same_instance(self):
        """同名熔断器返回同一实例"""
        manager = CircuitBreakerManager()
        b1 = manager.get_breaker('provider-a')
        b2 = manager.get_breaker('provider-a')
        assert b1 is b2

    def test_get_all_status(self):
        """获取所有熔断器状态"""
        manager = CircuitBreakerManager()
        manager.get_breaker('a')
        manager.get_breaker('b')
        statuses = manager.get_all_status()
        assert len(statuses) == 2
        names = {s['name'] for s in statuses}
        assert names == {'a', 'b'}

    def test_reset_all(self):
        """重置所有熔断器"""
        manager = CircuitBreakerManager()
        b1 = manager.get_breaker('a')
        b2 = manager.get_breaker('b')
        # 触发熔断
        for _ in range(10):
            b1.record_failure()
            b2.record_failure()
        assert b1.state == CircuitState.OPEN
        assert b2.state == CircuitState.OPEN

        manager.reset_all()
        assert b1.state == CircuitState.CLOSED
        assert b2.state == CircuitState.CLOSED
