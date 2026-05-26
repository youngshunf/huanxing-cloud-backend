"""
Marketplace Admin Sync API

Admin endpoints for managing marketplace syncs.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.app.marketplace.service.clawhub_sync_service import clawhub_sync_service
from backend.app.marketplace.service.github_sync_service import github_sync_service
from backend.app.marketplace.service.github_app_sync_service import github_app_sync_service
from backend.app.marketplace.service.package_service import package_service
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter(dependencies=[DependsJwtAuth])


class SyncRequest(BaseModel):
    """Sync request model"""
    force: bool = False
    skill_ids: list[str] | None = None


@router.post('/github', summary='Trigger GitHub sync')
async def trigger_github_sync(
    db: CurrentSession,
    request: SyncRequest
):
    """Trigger sync from GitHub repository"""
    result = await github_sync_service.sync_from_github(
        db=db,
        force=request.force
    )
    return result


@router.post('/github/apps', summary='Trigger GitHub app template sync')
async def trigger_github_app_sync(
    db: CurrentSession,
    request: SyncRequest
):
    """Trigger app template sync from GitHub repository"""
    result = await github_app_sync_service.sync_from_github(
        db=db,
        force=request.force
    )
    return result


@router.post('/clawhub', summary='Trigger ClawHub sync')
async def trigger_clawhub_sync(
    db: CurrentSession,
    request: SyncRequest
):
    """Trigger sync from ClawHub marketplace"""
    result = await clawhub_sync_service.sync_from_clawhub(
        db=db,
        force=request.force,
        skill_ids=request.skill_ids
    )
    return result


@router.get('/status', summary='Get sync status')
async def get_sync_status(db: CurrentSession):
    """Get current sync status and statistics"""
    # This would query the sync_log table for recent syncs
    # For now, return a simple status
    return {
        'github': {
            'status': 'idle',
            'last_sync': None
        },
        'clawhub': {
            'status': 'idle',
            'last_sync': None
        }
    }


@router.delete('/cache', summary='Clear package cache')
async def clear_package_cache(
    skill_id: str | None = Query(None, description='Skill ID (clear all if not specified)')
):
    """Clear package cache"""
    await package_service.clear_cache(skill_id)
    return {'success': True, 'message': 'Cache cleared'}


@router.get('/cache/stats', summary='Get cache statistics')
async def get_cache_stats():
    """Get package cache statistics"""
    stats = await package_service.get_cache_stats()
    return stats
