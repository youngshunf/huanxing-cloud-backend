from fastapi import APIRouter

from backend.common.response.response_schema import response_base

router = APIRouter()


@router.get('', summary='RAGFlow 凭据管理列表')
async def list_ragflow_credentials():
    return response_base.success(data={'items': []})
