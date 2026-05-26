#!/usr/bin/env python3
"""后端核心功能端到端测试

测试后端服务的核心功能，不依赖外部服务
"""

import sys
import requests
from datetime import datetime

sys.path.insert(0, '/Users/mac/openclaw-workspace/huanxing/huanxing-project/huanxing-cloud-backend')

from tests.test_auth_helper import get_test_headers

BASE_URL = "http://127.0.0.1:8020"


def test_backend_health():
    """测试后端服务健康状态"""
    print("\n" + "=" * 60)
    print("测试 1: 后端服务健康检查")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False


def test_marketplace_skills_list():
    """测试技能市场列表 API"""
    print("\n" + "=" * 60)
    print("测试 4: 技能市场列表")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/marketplace/open/skills/search",
            params={"q": "", "page": 1, "page_size": 10}
        )

        if response.status_code == 200:
            result = response.json()
            skills = result.get('data', {}).get('items', [])
            total = result.get('data', {}).get('total', 0)
            print(f"✅ 获取技能列表成功: {len(skills)} 个技能 (总计 {total})")
            return True
        else:
            print(f"❌ 获取技能列表失败: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("唤星后端端到端测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BASE_URL}")

    results = []

    # 运行测试
    results.append(("后端健康检查", test_backend_health()))

    # 生成一次认证 token，避免事件循环冲突
    print("\n生成测试认证 token...")
    try:
        headers = get_test_headers(user_id=1)
        print("✅ 认证 token 生成成功")
    except Exception as e:
        print(f"❌ 认证 token 生成失败: {e}")
        print("\n跳过需要认证的测试")
        results.append(("集成应用列表", False))
        results.append(("集成连接状态", False))
        results.append(("技能市场列表", test_marketplace_skills_list()))
    else:
        # 使用同一个 headers 运行需要认证的测试
        results.append(("集成应用列表", test_integration_list_apps_with_headers(headers)))
        results.append(("集成连接状态", test_integration_connection_status_with_headers(headers)))
        results.append(("技能市场列表", test_marketplace_skills_list()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)

    return passed == total


def test_integration_list_apps_with_headers(headers):
    """测试集成应用列表 API（使用预生成的 headers）"""
    print("\n" + "=" * 60)
    print("测试 2: 集成应用列表")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/apps/list",
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            apps = result.get('data', {}).get('apps', [])
            print(f"✅ 获取应用列表成功: {len(apps)} 个应用")
            for app in apps:
                print(f"  - {app.get('app_id')}: {app.get('app_name')}")
            return True
        else:
            print(f"❌ 获取应用列表失败: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_integration_connection_status_with_headers(headers):
    """测试集成连接状态 API（使用预生成的 headers）"""
    print("\n" + "=" * 60)
    print("测试 3: 集成连接状态")
    print("=" * 60)

    app_id = "clawhub"

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/status",
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            connected = result.get('data', {}).get('connected', False)
            print(f"✅ 获取连接状态成功: connected={connected}")
            return True
        else:
            print(f"❌ 获取连接状态失败: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
