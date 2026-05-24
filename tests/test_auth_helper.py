"""测试认证辅助工具

用于生成测试用的 JWT token，绕过认证进行端到端测试
"""
import asyncio
import uuid
from datetime import timedelta

from backend.common.security.jwt import jwt_encode
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.timezone import timezone


async def create_test_token_async(user_id: int = 1, owner_id: str = "owner_test_001") -> str:
    """创建测试用的 JWT token（异步版本，会存储到 Redis）

    Args:
        user_id: 用户 ID
        owner_id: Owner ID

    Returns:
        JWT token 字符串
    """
    expire = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
    session_uuid = str(uuid.uuid4())

    access_token = jwt_encode({
        'session_uuid': session_uuid,
        'exp': timezone.to_utc(expire).timestamp(),
        'sub': str(user_id),
    })

    # 存储到 Redis（与 create_access_token 相同的逻辑）
    await redis_client.setex(
        f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{session_uuid}',
        settings.TOKEN_EXPIRE_SECONDS,
        access_token,
    )

    return access_token


def create_test_token(user_id: int = 1, owner_id: str = "owner_test_001") -> str:
    """创建测试用的 JWT token（同步版本）

    Args:
        user_id: 用户 ID
        owner_id: Owner ID

    Returns:
        JWT token 字符串
    """
    return asyncio.run(create_test_token_async(user_id, owner_id))


def get_test_headers(user_id: int = 1, owner_id: str = "owner_test_001") -> dict:
    """获取测试用的请求头

    Args:
        user_id: 用户 ID
        owner_id: Owner ID

    Returns:
        包含 Authorization 的请求头字典
    """
    token = create_test_token(user_id, owner_id)
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


if __name__ == "__main__":
    # 生成测试 token
    token = create_test_token()
    print("Test Token:")
    print(token)
    print("\nTest Headers:")
    headers = get_test_headers()
    print(headers)
