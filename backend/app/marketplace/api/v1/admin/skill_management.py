"""
Marketplace Admin Skill Management API

Admin endpoints for managing marketplace skills.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao
from backend.app.marketplace.service.translation_service import translation_service
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter(dependencies=[DependsJwtAuth])


class TranslateRequest(BaseModel):
    """Translation request model"""
    skill_id: str
    force: bool = False


class ApprovalRequest(BaseModel):
    """Skill approval request model"""
    skill_id: str
    approved: bool
    reason: str | None = None


@router.post('/translate', summary='Translate skill metadata')
async def translate_skill(
    db: CurrentSession,
    request: TranslateRequest
):
    """Manually trigger translation for a skill"""
    # Get skill
    skill = await marketplace_skill_dao.get_by_id(db, request.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')

    # Check if translation needed
    if not request.force:
        if skill.name_en and skill.name_zh and skill.description_en and skill.description_zh:
            return {
                'success': True,
                'message': 'Skill already translated',
                'translated': False
            }

    # Determine source text
    name = skill.name_en or skill.name_zh
    description = skill.description_en or skill.description_zh

    if not name:
        raise HTTPException(status_code=400, detail='Skill has no name to translate')

    # Translate
    translated = await translation_service.translate_skill_metadata(
        name=name,
        description=description
    )

    # Update skill
    await marketplace_skill_dao.update(db, skill.id, {
        'name_en': translated['name_en'],
        'name_zh': translated['name_zh'],
        'description_en': translated['description_en'],
        'description_zh': translated['description_zh'],
        'source_language': translated['source_language'],
        'translation_status': 'completed'
    })

    return {
        'success': True,
        'message': 'Translation completed',
        'translated': True,
        'result': translated
    }


@router.post('/approve', summary='Approve or reject skill')
async def approve_skill(
    db: CurrentSession,
    request: ApprovalRequest
):
    """Approve or reject a skill for publication"""
    # Get skill
    skill = await marketplace_skill_dao.get_by_id(db, request.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')

    # Update approval status
    await marketplace_skill_dao.update(db, skill.id, {
        'is_private': not request.approved,
        'approval_status': 'approved' if request.approved else 'rejected',
        'approval_reason': request.reason
    })

    return {
        'success': True,
        'message': f"Skill {'approved' if request.approved else 'rejected'}"
    }


@router.post('/{skill_id}/feature', summary='Feature a skill')
async def feature_skill(
    db: CurrentSession,
    skill_id: str,
    featured: bool = Query(True, description='Set featured status')
):
    """Mark a skill as featured"""
    # Get skill
    skill = await marketplace_skill_dao.get_by_id(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')

    # Update featured status
    await marketplace_skill_dao.update(db, skill.id, {
        'is_featured': featured
    })

    return {
        'success': True,
        'message': f"Skill {'featured' if featured else 'unfeatured'}"
    }


@router.get('/stats', summary='Get marketplace statistics')
async def get_marketplace_stats(db: CurrentSession):
    """Get marketplace statistics"""
    from sqlalchemy import func, select
    from backend.app.marketplace.model.marketplace_skill import MarketplaceSkill

    # Total skills
    total_query = select(func.count(MarketplaceSkill.id))
    total_result = await db.execute(total_query)
    total_skills = total_result.scalar() or 0

    # Public skills
    public_query = select(func.count(MarketplaceSkill.id)).where(
        MarketplaceSkill.is_private == False
    )
    public_result = await db.execute(public_query)
    public_skills = public_result.scalar() or 0

    # Official skills
    official_query = select(func.count(MarketplaceSkill.id)).where(
        MarketplaceSkill.is_official == True
    )
    official_result = await db.execute(official_query)
    official_skills = official_result.scalar() or 0

    # Total downloads
    downloads_query = select(func.sum(MarketplaceSkill.download_count))
    downloads_result = await db.execute(downloads_query)
    total_downloads = downloads_result.scalar() or 0

    # Total stars
    stars_query = select(func.sum(MarketplaceSkill.star_count))
    stars_result = await db.execute(stars_query)
    total_stars = stars_result.scalar() or 0

    return {
        'total_skills': total_skills,
        'public_skills': public_skills,
        'official_skills': official_skills,
        'total_downloads': total_downloads,
        'total_stars': total_stars
    }
