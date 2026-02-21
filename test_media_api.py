#!/usr/bin/env python3
"""
媒体生成 API 测试脚本
测试图像和视频生成接口
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8020/api/v1/llm/proxy/v1"
API_KEY = "sk-cf-test-key-123456"  # 测试用的 API Key

async def test_image_generation():
    """测试图像生成接口"""
    print("\n" + "="*60)
    print("测试 1: 图像生成 (DALL-E 3)")
    print("="*60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/images/generations",
            headers={
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "model": "dall-e-3",
                "prompt": "A beautiful sunset over mountains",
                "size": "1024x1024",
                "quality": "standard",
                "n": 1
            }
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            data = response.json()
            task_id = data.get("id")
            print(f"\n✅ 任务创建成功，任务 ID: {task_id}")
            return task_id
        else:
            print(f"\n❌ 任务创建失败")
            return None

async def test_image_status(task_id: str):
    """测试查询图像生成状态"""
    print("\n" + "="*60)
    print(f"测试 2: 查询图像生成状态 (任务 ID: {task_id})")
    print("="*60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/images/generations/{task_id}",
            headers={"x-api-key": API_KEY}
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def test_video_generation():
    """测试视频生成接口"""
    print("\n" + "="*60)
    print("测试 3: 视频生成 (可灵)")
    print("="*60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/videos/generations",
            headers={
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "model": "kling-v1",
                "prompt": "A cat playing with a ball",
                "duration": 5
            }
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            data = response.json()
            task_id = data.get("id")
            print(f"\n✅ 任务创建成功，任务 ID: {task_id}")
            return task_id
        else:
            print(f"\n❌ 任务创建失败")
            return None

async def test_video_status(task_id: str):
    """测试查询视频生成状态"""
    print("\n" + "="*60)
    print(f"测试 4: 查询视频生成状态 (任务 ID: {task_id})")
    print("="*60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/videos/generations/{task_id}",
            headers={"x-api-key": API_KEY}
        )

        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

async def main():
    print("\n" + "="*60)
    print("媒体生成 API 测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    try:
        # 测试图像生成
        image_task_id = await test_image_generation()
        if image_task_id:
            await asyncio.sleep(2)
            await test_image_status(image_task_id)

        # 测试视频生成
        video_task_id = await test_video_generation()
        if video_task_id:
            await asyncio.sleep(2)
            await test_video_status(video_task_id)

        print("\n" + "="*60)
        print("测试完成")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
