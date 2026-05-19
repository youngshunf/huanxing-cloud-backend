from fastapi import APIRouter

from backend.common.response.response_schema import response_base

router = APIRouter()


@router.get('', summary='活跃工作区管理列表')
async def list_user_active_workspaces():
    return response_base.success(data={'items': []})
