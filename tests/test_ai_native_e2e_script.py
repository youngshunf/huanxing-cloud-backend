"""
测试 AI-Native E2E 脚本的结构和基础功能
"""

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "ai_native_e2e.py"


def load_script_module():
    """加载 E2E 脚本模块"""
    spec = importlib.util.spec_from_file_location("ai_native_e2e", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_exists():
    """测试脚本文件存在"""
    assert SCRIPT_PATH.exists(), f"E2E 脚本不存在: {SCRIPT_PATH}"


def test_script_has_main():
    """测试脚本有 main 函数"""
    module = load_script_module()
    assert hasattr(module, "main"), "脚本缺少 main 函数"
    assert callable(module.main), "main 不是可调用函数"


def test_script_has_runner_class():
    """测试脚本有 E2ETestRunner 类"""
    module = load_script_module()
    assert hasattr(module, "E2ETestRunner"), "脚本缺少 E2ETestRunner 类"


def test_runner_has_required_methods():
    """测试 Runner 有必需的方法"""
    module = load_script_module()
    runner = module.E2ETestRunner()

    required_methods = [
        "run_all_tests",
        "test_daemon_health",
        "test_backend_health",
        "test_user_login",
        "test_agent_jwt_issued",
        "test_knowledge_app_published",
        "test_capabilities_discovery",
        "test_knowledge_search_call",
        "test_audit_written",
        "log_step",
        "summarize_results",
        "save_evidence",
    ]

    for method in required_methods:
        assert hasattr(runner, method), f"Runner 缺少方法: {method}"
        assert callable(getattr(runner, method)), f"{method} 不是可调用方法"


def test_runner_initializes_evidence():
    """测试 Runner 初始化证据结构"""
    module = load_script_module()
    runner = module.E2ETestRunner()

    assert hasattr(runner, "evidence"), "Runner 缺少 evidence 属性"
    assert isinstance(runner.evidence, dict), "evidence 不是字典"
    assert "test_run_id" in runner.evidence, "evidence 缺少 test_run_id"
    assert "start_time" in runner.evidence, "evidence 缺少 start_time"
    assert "steps" in runner.evidence, "evidence 缺少 steps"
    assert isinstance(runner.evidence["steps"], list), "steps 不是列表"


def test_log_step_records_evidence():
    """测试 log_step 记录证据"""
    module = load_script_module()
    runner = module.E2ETestRunner()

    initial_count = len(runner.evidence["steps"])

    runner.log_step("test_step", True, {"key": "value"})

    assert len(runner.evidence["steps"]) == initial_count + 1, "步骤未记录"

    step = runner.evidence["steps"][-1]
    assert step["name"] == "test_step", "步骤名称不正确"
    assert step["success"] is True, "步骤成功状态不正确"
    assert "timestamp" in step, "步骤缺少时间戳"
    assert step["details"]["key"] == "value", "步骤详情不正确"
