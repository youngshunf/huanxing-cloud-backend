from fastapi import APIRouter

from backend.common.response.response_schema import response_base

router = APIRouter()


@router.get('', summary='企业邀请码管理列表')
async def list_enterprise_invite_codes():
    return response_base.success(data={'items': []})
