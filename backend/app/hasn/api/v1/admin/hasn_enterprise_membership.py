from fastapi import APIRouter

from backend.common.response.response_schema import response_base

router = APIRouter()


@router.get('', summary='企业成员管理列表')
async def list_enterprise_memberships():
    return response_base.success(data={'items': []})
