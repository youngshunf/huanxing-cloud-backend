"""
HASN 身份注册 & 认证 API
对应设计文档: 07-API设计.md §二 / 01-身份体系.md §五
"""
import hashlib
import secrets
from uuid import uuid4

from fastapi import APIRouter, Request

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.response.response_code import CustomResponse
from backend.database.db import CurrentSession
from backend.database.redis import redis_client
from backend.app.hasn_core.crud.crud_human import crud_hasn_human
from backend.app.hasn_core.crud.crud_agent import crud_hasn_agent
from backend.app.hasn_core.service.hasn_auth import hasn_create_jwt
from backend.app.hasn_core.schema.hasn_identity import (
    HasnRegisterReq, HasnRegisterResp,
    HasnHumanOut, HasnAgentOut,
)

router = APIRouter(prefix="/auth", tags=["HASN Auth"])

STAR_ID_COUNTER_KEY = "hasn:star_id_counter"
STAR_ID_START = 100001


def _generate_hasn_id(entity_type: str) -> str:
    """生成 hasn_id: h_uuid 或 a_uuid"""
    prefix = "h_" if entity_type == "human" else "a_"
    return f"{prefix}{uuid4().hex[:24]}"


async def _allocate_star_id() -> str:
    """原子自增分配唤星号 (MVP简化版，无号池表)"""
    val = await redis_client.incr(STAR_ID_COUNTER_KEY)
    # 首次使用时 val=1，需要加上起始偏移
    if val < STAR_ID_START:
        await redis_client.set(STAR_ID_COUNTER_KEY, STAR_ID_START)
        val = STAR_ID_START
    return str(val)


def _generate_api_key() -> tuple[str, str, str]:
    """生成 Agent API Key → (明文key, sha256_hash, prefix)"""
    raw = f"hasn_ak_{secrets.token_hex(32)}"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    prefix = raw[:16]
    return raw, key_hash, prefix


@router.post("/register", summary="注册 HASN 身份 (内部调用)")
async def register(
    obj_in: HasnRegisterReq,
    db: CurrentSession,
) -> ResponseModel:
    """
    内部注册接口 — Guardian/唤星系统调用
    一次性创建 Human + 主Agent
    对应设计文档 07-API §2.1: POST /api/v1/internal/register
    """
    # 1. 检查是否已注册
    existing = await crud_hasn_human.get_by_huanxing_user_id(db, obj_in.huanxing_user_id)
    if existing:
        return response_base.fail(res=CustomResponse(code=400, msg=f"用户 {obj_in.huanxing_user_id} 已注册 HASN 身份"))

    # 2. 生成 Human 身份
    human_id = _generate_hasn_id("human")
    star_id = await _allocate_star_id()

    phone_hash = None
    if obj_in.phone:
        phone_hash = hashlib.sha256(obj_in.phone.encode()).hexdigest()

    human = await crud_hasn_human.create(
        db,
        id=human_id,
        star_id=star_id,
        huanxing_user_id=obj_in.huanxing_user_id,
        name=obj_in.nickname,
        phone=obj_in.phone,  # TODO: MVP先明文，后续AES加密
        phone_hash=phone_hash,
    )

    # 3. 生成 Agent 身份
    agent_id = _generate_hasn_id("agent")
    agent_star_id = f"{star_id}#{obj_in.agent_name}"
    api_key_raw, api_key_hash, api_key_prefix = _generate_api_key()

    agent = await crud_hasn_agent.create(
        db,
        id=agent_id,
        star_id=agent_star_id,
        owner_id=human_id,
        name=obj_in.agent_name,
        api_key_hash=api_key_hash,
        api_key_prefix=api_key_prefix,
    )

    await db.commit()

    # 4. 签发 JWT
    jwt_token = hasn_create_jwt(human_id, star_id, "human")

    # 5. 返回结果（对齐设计文档07 §2.1 Response 201）
    return response_base.success(data=HasnRegisterResp(
        human=HasnHumanOut(
            hasn_id=human.id,
            star_id=human.star_id,
            name=human.name,
            jwt_token=jwt_token,
            refresh_token=None,  # TODO: Refresh Token
        ),
        agent=HasnAgentOut(
            hasn_id=agent.id,
            star_id=agent.star_id,
            name=agent.name,
            api_key=api_key_raw,  # 仅注册时返回明文
        ),
    ).model_dump())
