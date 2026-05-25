"""
Marketplace Skills Open API

Public API for browsing and downloading skills.
"""
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from backend.app.marketplace.crud.crud_marketplace_download_history import marketplace_download_history_dao
from backend.app.marketplace.service.package_service import package_service
from backend.app.marketplace.service.search_service import search_service
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('/search', summary='Search skills')
async def search_skills(
    db: CurrentSession,
    keyword: str | None = Query(None, description='Search keyword'),
    category: str | None = Query(None, description='Category filter'),
    tags: str | None = Query(None, description='Comma-separated tags'),
    lang: str = Query('zh', description='Language (zh/en)'),
    page: int = Query(1, ge=1, description='Page number'),
    page_size: int = Query(20, ge=1, le=100, description='Items per page'),
    sort_by: str = Query('popular', description='Sort by (popular/latest/downloads/stars)')
):
    """Search skills with filters"""
    tag_list = tags.split(',') if tags else None

    result = await search_service.search_skills(
        db=db,
        keyword=keyword,
        category=category,
        tags=tag_list,
        lang=lang,
        page=page,
        page_size=page_size,
        sort_by=sort_by
    )

    return result


@router.get('/skills/{skill_id}', summary='Get skill detail')
async def get_skill_detail(
    db: CurrentSession,
    skill_id: str,
    lang: str = Query('zh', description='Language (zh/en)')
):
    """Get skill detail by ID"""
    skill = await search_service.get_skill_detail(db, skill_id, lang)

    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')

    return skill


@router.get('/skills/{skill_id}/download', summary='Download skill package')
async def download_skill_open(
    db: CurrentSession,
    skill_id: str,
    version: str | None = Query(None, description='Version (use latest if not specified)')
):
    """Download skill package as zip file"""
    try:
        # Get package
        package_path, package_hash = await package_service.get_skill_package(
            db, skill_id, version
        )

        # Record download
        await marketplace_download_history_dao.create(db, {
            'skill_id': skill_id,
            'version': version or 'latest',
            'user_id': None,  # Anonymous download
            'ip_address': None,
            'user_agent': None
        })

        # Return file stream
        file_stream = package_service.get_package_stream(package_path)
        filename = f"{skill_id.replace('/', '_')}_{version or 'latest'}.zip"

        return StreamingResponse(
            file_stream,
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'X-Package-Hash': package_hash
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to download skill: {str(e)}')


@router.get('/popular', summary='Get popular skills')
async def get_popular_skills(
    db: CurrentSession,
    lang: str = Query('zh', description='Language (zh/en)'),
    limit: int = Query(10, ge=1, le=50, description='Number of skills')
):
    """Get popular skills"""
    skills = await search_service.get_popular_skills(db, lang, limit)
    return {'items': skills}


@router.get('/official', summary='Get official skills')
async def get_official_skills(
    db: CurrentSession,
    lang: str = Query('zh', description='Language (zh/en)'),
    limit: int = Query(10, ge=1, le=50, description='Number of skills')
):
    """Get official skills"""
    skills = await search_service.get_official_skills(db, lang, limit)
    return {'items': skills}


@router.get('/categories', summary='Get all categories')
async def get_categories(
    db: CurrentSession,
    lang: str = Query('zh', description='Language (zh/en)')
):
    """Get all categories with skill counts"""
    categories = await search_service.get_categories(db, lang)
    return {'items': categories}
