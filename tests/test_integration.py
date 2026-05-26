#!/usr/bin/env python3
"""Third-party Integration System E2E Test

Test the complete integration flow:
1. List available apps
2. Connect to ClawHub
3. Check connection status
4. Get iframe URL
5. Disconnect from ClawHub
"""

import sys
import time
import requests
from datetime import datetime

sys.path.insert(0, '/Users/mac/openclaw-workspace/huanxing/huanxing-project/huanxing-cloud-backend')

from tests.test_auth_helper import get_test_headers

BASE_URL = "http://127.0.0.1:8020"


def test_integration_flow():
    """Test complete integration flow"""
    print("=" * 60)
    print("Third-party Integration System E2E Test")
    print("=" * 60)

    # Get test auth headers
    headers = get_test_headers(user_id=1)
    print(f"\nAuth Token: {headers['Authorization'][:50]}...")

    # Step 1: List available apps
    print("\n" + "=" * 60)
    print("Step 1: List Available Apps")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/apps/list",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ List apps successful")
            result = response.json()
            print(f"Response: {result}")
            apps = result.get('data', {}).get('apps', [])
            print(f"  Available apps: {len(apps)}")
            for app in apps:
                print(f"    - {app.get('app_id')}: {app.get('app_name')}")
        else:
            print(f"❌ List apps failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Step 2: Check initial connection status
    print("\n" + "=" * 60)
    print("Step 2: Check Initial Connection Status")
    print("=" * 60)

    app_id = "clawhub"
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/status",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Status check successful")
            result = response.json()
            print(f"Response: {result}")
            connected = result.get('data', {}).get('connected', False)
            print(f"  Connected: {connected}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Step 3: Connect to ClawHub
    print("\n" + "=" * 60)
    print("Step 3: Connect to ClawHub")
    print("=" * 60)

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/connect",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Connection successful")
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            # If connection fails, skip remaining tests
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

    # Step 4: Check connection status after connecting
    print("\n" + "=" * 60)
    print("Step 4: Check Connection Status After Connecting")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/status",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Status check successful")
            result = response.json()
            print(f"Response: {result}")
            connected = result.get('data', {}).get('connected', False)
            print(f"  Connected: {connected}")
            if connected:
                print("  ✅ Connection verified")
            else:
                print("  ❌ Connection not verified")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Step 5: Get iframe URL
    print("\n" + "=" * 60)
    print("Step 5: Get Iframe URL")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/iframe-url",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Get iframe URL successful")
            result = response.json()
            print(f"Response: {result}")
            iframe_url = result.get('data', {}).get('iframe_url')
            login_token = result.get('data', {}).get('login_token')
            print(f"  Iframe URL: {iframe_url}")
            print(f"  Login Token: {login_token[:20]}..." if login_token else "  Login Token: None")
        else:
            print(f"❌ Get iframe URL failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Step 6: Disconnect from ClawHub
    print("\n" + "=" * 60)
    print("Step 6: Disconnect from ClawHub")
    print("=" * 60)

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/disconnect",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Disconnection successful")
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"❌ Disconnection failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Step 7: Verify disconnection
    print("\n" + "=" * 60)
    print("Step 7: Verify Disconnection")
    print("=" * 60)

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/integration/app/{app_id}/status",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Status check successful")
            result = response.json()
            print(f"Response: {result}")
            connected = result.get('data', {}).get('connected', False)
            print(f"  Connected: {connected}")
            if not connected:
                print("  ✅ Disconnection verified")
            else:
                print("  ❌ Still connected")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n" + "=" * 60)
    print("Test Completed")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_integration_flow()
    sys.exit(0 if success else 1)
