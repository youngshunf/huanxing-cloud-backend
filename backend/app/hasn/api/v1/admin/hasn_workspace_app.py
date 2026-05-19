from fastapi import APIRouter

from backend.common.response.response_schema import response_base

router = APIRouter()


@router.get('', summary='工作空间应用管理列表')
async def list_workspace_apps():
    return response_base.success(data={'items': []})
