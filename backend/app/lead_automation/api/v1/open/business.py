from __future__ import annotations

from fastapi import APIRouter

from backend.app.lead_automation.service.firecrawl_client import DEFAULT_FIRECRAWL_BASE_URL
from backend.common.response.response_schema import ResponseModel, response_base

router = APIRouter()


@router.get('/healthz', summary='健康检查')
async def healthz() -> ResponseModel:
    return response_base.success(data={'status': 'ok', 'firecrawl_base_url': DEFAULT_FIRECRAWL_BASE_URL})
