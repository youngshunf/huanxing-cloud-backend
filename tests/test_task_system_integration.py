"""任务系统集成测试

测试 Phase 1 和 Phase 2 的后端 API 功能：
- Session API (6个端点)
- Task API (7个端点)
"""

import pytest
import requests
from datetime import datetime, timezone
import ulid


BASE_URL = "http://127.0.0.1:8020"
API_PREFIX = "/api/v1/hasn"


@pytest.fixture
def auth_headers():
    """获取认证 headers（需要先登录）"""
    # TODO: 实现登录逻辑获取 JWT token
    # 暂时使用测试 token
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_session_id():
    """生成测试 session_id"""
    return f"sess_test_{ulid.new().str}"


@pytest.fixture
def test_task_id():
    """生成测试 task_id"""
    return f"task_test_{ulid.new().str}"


class TestSessionAPI:
    """测试 Session API"""

    def test_01_upsert_session(self, auth_headers, test_session_id):
        """测试创建/更新 Session"""
        url = f"{BASE_URL}{API_PREFIX}/sessions/upsert"
        payload = {
            "session_id": test_session_id,
            "conversation_id": None,
            "owner_id": "owner_test_001",
            "hasn_id": "agent_test_001",
            "session_kind": "task",
            "session_scope": "conversation_visible",
            "session_status": "active",
            "origin_type": "task_run",
            "origin_ref": "task_run_001",
            "title": "测试任务 Session",
            "summary_checkpoint_json": {}
        }

        response = requests.post(url, json=payload, headers=auth_headers)
        print(f"\n[Session Upsert] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code in [200, 201], f"创建 Session 失败: {response.text}"
        data = response.json()
        assert data.get("session_id") == test_session_id

    def test_02_get_sessions_list(self, auth_headers):
        """测试查询 Session 列表"""
        url = f"{BASE_URL}{API_PREFIX}/sessions"
        params = {
            "session_kind": "task,interactive",
            "page": 1,
            "page_size": 20
        }

        response = requests.get(url, params=params, headers=auth_headers)
        print(f"\n[Session List] Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        assert response.status_code == 200, f"查询 Session 列表失败: {response.text}"
        data = response.json()
        assert "sessions" in data or "items" in data

    def test_03_get_session_detail(self, auth_headers, test_session_id):
        """测试查询 Session 详情"""
        # 先创建 session
        self.test_01_upsert_session(auth_headers, test_session_id)

        url = f"{BASE_URL}{API_PREFIX}/sessions/{test_session_id}"
        response = requests.get(url, headers=auth_headers)
        print(f"\n[Session Detail] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"查询 Session 详情失败: {response.text}"
        data = response.json()
        assert data.get("session_id") == test_session_id

    def test_04_update_session_summary(self, auth_headers, test_session_id):
        """测试更新 Session 摘要"""
        # 先创建 session
        self.test_01_upsert_session(auth_headers, test_session_id)

        url = f"{BASE_URL}{API_PREFIX}/sessions/{test_session_id}/summary"
        payload = {
            "summary_checkpoint_json": {
                "last_message_id": "msg_001",
                "summary": "任务执行中..."
            }
        }

        response = requests.post(url, json=payload, headers=auth_headers)
        print(f"\n[Session Summary Update] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"更新 Session 摘要失败: {response.text}"

    def test_05_close_session(self, auth_headers, test_session_id):
        """测试关闭 Session"""
        # 先创建 session
        self.test_01_upsert_session(auth_headers, test_session_id)

        url = f"{BASE_URL}{API_PREFIX}/sessions/{test_session_id}/close"
        payload = {
            "session_status": "completed",
            "closed_at": datetime.now(timezone.utc).isoformat()
        }

        response = requests.post(url, json=payload, headers=auth_headers)
        print(f"\n[Session Close] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"关闭 Session 失败: {response.text}"

    def test_06_get_session_messages(self, auth_headers, test_session_id):
        """测试查询 Session 消息列表"""
        url = f"{BASE_URL}{API_PREFIX}/sessions/{test_session_id}/messages"
        params = {
            "page": 1,
            "page_size": 50
        }

        response = requests.get(url, params=params, headers=auth_headers)
        print(f"\n[Session Messages] Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        assert response.status_code == 200, f"查询 Session 消息失败: {response.text}"


class TestTaskAPI:
    """测试 Task API"""

    def test_01_create_task(self, auth_headers, test_task_id):
        """测试创建任务"""
        url = f"{BASE_URL}{API_PREFIX}/tasks"
        payload = {
            "task_id": test_task_id,
            "owner_id": "owner_test_001",
            "name": "测试定时任务",
            "agent_id": "agent_test_001",
            "prompt": "分析今日A股市场",
            "schedule_type": "cron",
            "schedule_config": {"cron": "0 9 * * *"},
            "enabled": True
        }

        response = requests.post(url, json=payload, headers=auth_headers)
        print(f"\n[Task Create] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code in [200, 201], f"创建任务失败: {response.text}"
        data = response.json()
        assert data.get("task_id") == test_task_id

    def test_02_get_tasks_list(self, auth_headers):
        """测试查询任务列表"""
        url = f"{BASE_URL}{API_PREFIX}/tasks"
        params = {
            "enabled": True,
            "page": 1,
            "page_size": 20
        }

        response = requests.get(url, params=params, headers=auth_headers)
        print(f"\n[Task List] Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        assert response.status_code == 200, f"查询任务列表失败: {response.text}"

    def test_03_get_task_detail(self, auth_headers, test_task_id):
        """测试查询任务详情"""
        # 先创建任务
        self.test_01_create_task(auth_headers, test_task_id)

        url = f"{BASE_URL}{API_PREFIX}/tasks/{test_task_id}"
        response = requests.get(url, headers=auth_headers)
        print(f"\n[Task Detail] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"查询任务详情失败: {response.text}"
        data = response.json()
        assert data.get("task_id") == test_task_id

    def test_04_update_task(self, auth_headers, test_task_id):
        """测试更新任务"""
        # 先创建任务
        self.test_01_create_task(auth_headers, test_task_id)

        url = f"{BASE_URL}{API_PREFIX}/tasks/{test_task_id}"
        payload = {
            "name": "测试定时任务（已更新）",
            "prompt": "分析今日A股市场（更新版）"
        }

        response = requests.put(url, json=payload, headers=auth_headers)
        print(f"\n[Task Update] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"更新任务失败: {response.text}"

    def test_05_enable_task(self, auth_headers, test_task_id):
        """测试启用任务"""
        # 先创建任务
        self.test_01_create_task(auth_headers, test_task_id)

        url = f"{BASE_URL}{API_PREFIX}/tasks/{test_task_id}/enable"
        response = requests.post(url, headers=auth_headers)
        print(f"\n[Task Enable] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"启用任务失败: {response.text}"

    def test_06_disable_task(self, auth_headers, test_task_id):
        """测试禁用任务"""
        # 先创建任务
        self.test_01_create_task(auth_headers, test_task_id)

        url = f"{BASE_URL}{API_PREFIX}/tasks/{test_task_id}/disable"
        response = requests.post(url, headers=auth_headers)
        print(f"\n[Task Disable] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 200, f"禁用任务失败: {response.text}"

    def test_07_delete_task(self, auth_headers, test_task_id):
        """测试删除任务"""
        # 先创建任务
        self.test_01_create_task(auth_headers, test_task_id)

        url = f"{BASE_URL}{API_PREFIX}/tasks/{test_task_id}"
        response = requests.delete(url, headers=auth_headers)
        print(f"\n[Task Delete] Status: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code in [200, 204], f"删除任务失败: {response.text}"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
