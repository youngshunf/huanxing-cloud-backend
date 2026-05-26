"""
ClawHub Sync Service

Syncs skills from ClawHub marketplace to Huanxing marketplace.
"""
import json
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao
from backend.app.marketplace.crud.crud_marketplace_skill_version import marketplace_skill_version_dao
from backend.app.marketplace.crud.crud_marketplace_sync_log import marketplace_sync_log_dao
from backend.app.marketplace.service.translation_service import translation_service
from backend.common.log import log
from backend.core.conf import settings


class ClawHubSyncService:
    """ClawHub sync service for marketplace skills"""

    def __init__(self):
        self.clawhub_api_url = getattr(settings, 'CLAWHUB_API_URL', 'https://hub.openclaw.com/api')
        self.sync_filters = {
            'official_only': True,  # Only sync official skills
            'min_downloads': 10,    # Minimum download count
            'min_stars': 5          # Minimum star count
        }

    async def sync_from_clawhub(
        self,
        db: AsyncSession,
        force: bool = False,
        skill_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Sync skills from ClawHub

        Args:
            db: Database session
            force: Force full sync (ignore last sync time)
            skill_ids: Specific skill IDs to sync (sync all if None)

        Returns:
            Sync result with statistics
        """
        sync_log_id = None
        try:
            # Create sync log
            sync_log = await marketplace_sync_log_dao.create(db, {
                'sync_type': 'clawhub',
                'status': 'in_progress',
                'started_at': datetime.now()
            })
            sync_log_id = sync_log.id

            # Fetch skills from ClawHub
            if skill_ids:
                skills_data = await self._fetch_specific_skills(skill_ids)
            else:
                skills_data = await self._fetch_all_skills()

            # Filter skills
            filtered_skills = self._filter_skills(skills_data)

            # Sync to database
            synced_count = 0
            failed_count = 0
            errors = []

            for skill_data in filtered_skills:
                try:
                    await self._sync_skill(db, skill_data)
                    synced_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"{skill_data.get('slug', 'unknown')}: {str(e)}")
                    log.error(f"Failed to sync skill {skill_data.get('slug')}: {e}")

            # Update sync log
            await marketplace_sync_log_dao.update(db, sync_log_id, {
                'status': 'success' if failed_count == 0 else 'partial',
                'items_synced': synced_count,
                'items_failed': failed_count,
                'error_message': '\n'.join(errors) if errors else None,
                'completed_at': datetime.now()
            })

            return {
                'success': True,
                'synced': synced_count,
                'failed': failed_count,
                'errors': errors
            }

        except Exception as e:
            log.error(f"ClawHub sync failed: {e}")

            # Update sync log
            if sync_log_id:
                await marketplace_sync_log_dao.update(db, sync_log_id, {
                    'status': 'failed',
                    'error_message': str(e),
                    'completed_at': datetime.now()
                })

            return {
                'success': False,
                'error': str(e)
            }

    async def _fetch_all_skills(self) -> list[dict[str, Any]]:
        """
        Fetch all skills from ClawHub API

        Returns:
            List of skill data
        """
        skills = []
        page = 1
        page_size = 50

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                try:
                    response = await client.get(
                        f"{self.clawhub_api_url}/skills",
                        params={
                            'page': page,
                            'pageSize': page_size,
                            'sortBy': 'popular'
                        }
                    )
                    response.raise_for_status()
                    data = response.json()

                    items = data.get('items', [])
                    if not items:
                        break

                    skills.extend(items)

                    # Check if there are more pages
                    if len(items) < page_size:
                        break

                    page += 1

                except Exception as e:
                    log.error(f"Failed to fetch skills from ClawHub (page {page}): {e}")
                    break

        return skills

    async def _fetch_specific_skills(self, skill_ids: list[str]) -> list[dict[str, Any]]:
        """
        Fetch specific skills from ClawHub API

        Args:
            skill_ids: List of skill IDs (slugs)

        Returns:
            List of skill data
        """
        skills = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for skill_id in skill_ids:
                try:
                    response = await client.get(f"{self.clawhub_api_url}/skills/{skill_id}")
                    response.raise_for_status()
                    skill_data = response.json()
                    skills.append(skill_data)
                except Exception as e:
                    log.error(f"Failed to fetch skill {skill_id} from ClawHub: {e}")

        return skills

    def _filter_skills(self, skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Filter skills based on sync criteria

        Args:
            skills: List of skill data

        Returns:
            Filtered list of skills
        """
        filtered = []

        for skill in skills:
            # Check official status
            if self.sync_filters['official_only'] and not skill.get('isOfficial', False):
                continue

            # Check download count
            if skill.get('downloadCount', 0) < self.sync_filters['min_downloads']:
                continue

            # Check star count
            if skill.get('starCount', 0) < self.sync_filters['min_stars']:
                continue

            filtered.append(skill)

        return filtered

    async def _sync_skill(self, db: AsyncSession, clawhub_skill: dict[str, Any]):
        """
        Sync a single skill from ClawHub to database

        Args:
            db: Database session
            clawhub_skill: ClawHub skill data
        """
        # Convert ClawHub format to Huanxing format
        skill_id = f"clawhub/{clawhub_skill['slug']}"

        # Check if skill exists
        existing_skill = await marketplace_skill_dao.get_by_skill_id(db, skill_id)

        # Translate name and description
        name = clawhub_skill.get('displayName') or clawhub_skill.get('slug')
        description = clawhub_skill.get('summary', '')

        translated = await translation_service.translate_skill_metadata(
            name=name,
            description=description
        )

        # Map category
        category = self._map_category(clawhub_skill.get('tags', []))

        # Prepare skill record
        skill_record = {
            'skill_id': skill_id,
            'name_en': translated['name_en'],
            'name_zh': translated['name_zh'],
            'description_en': translated['description_en'],
            'description_zh': translated['description_zh'],
            'source_language': translated['source_language'],
            'icon_url': clawhub_skill.get('icon'),
            'emoji': None,
            'author_name': clawhub_skill.get('author', {}).get('name'),
            'category': category,
            'tags': json.dumps(clawhub_skill.get('tags', [])),
            'pricing_type': 'free',
            'price': 0,
            'is_official': clawhub_skill.get('isOfficial', False),
            'is_private': False,
            'source': 'clawhub',
            'download_count': clawhub_skill.get('downloadCount', 0),
            'star_count': clawhub_skill.get('starCount', 0),
            'synced_at': datetime.now()
        }

        if existing_skill:
            # Update existing skill
            await marketplace_skill_dao.update(db, existing_skill.id, skill_record)
            db_skill_id = existing_skill.id
        else:
            # Create new skill
            new_skill = await marketplace_skill_dao.create(db, skill_record)
            db_skill_id = new_skill.id

        # Sync latest version
        versions = clawhub_skill.get('versions', [])
        if versions:
            latest_version = versions[0]
            await self._sync_skill_version(db, db_skill_id, latest_version)

    async def _sync_skill_version(
        self,
        db: AsyncSession,
        db_skill_id: int,
        version_data: dict[str, Any]
    ):
        """
        Sync a skill version

        Args:
            db: Database session
            db_skill_id: Database skill ID
            version_data: Version data from ClawHub
        """
        version = version_data.get('version', '1.0.0')

        # Check if version exists
        existing_version = await marketplace_skill_version_dao.get_by_skill_and_version(
            db, db_skill_id, version
        )

        # Translate changelog
        changelog = version_data.get('changelog', '')
        if changelog:
            translated_changelog = await translation_service.translate_skill_metadata(
                description=changelog
            )
            changelog_en = translated_changelog['description_en']
            changelog_zh = translated_changelog['description_zh']
        else:
            changelog_en = None
            changelog_zh = None

        # Prepare version record
        version_record = {
            'skill_id': db_skill_id,
            'version': version,
            'changelog_en': changelog_en,
            'changelog_zh': changelog_zh,
            'released_at': version_data.get('releasedAt')
        }

        if existing_version:
            # Update existing version
            await marketplace_skill_version_dao.update(db, existing_version.id, version_record)
        else:
            # Create new version
            await marketplace_skill_version_dao.create(db, version_record)

    def _map_category(self, tags: list[str]) -> str:
        """
        Map ClawHub tags to Huanxing category

        Args:
            tags: List of tags

        Returns:
            Category name
        """
        # Category mapping rules
        category_map = {
            'automation': ['automation', 'workflow', 'task'],
            'development': ['development', 'coding', 'programming', 'git'],
            'productivity': ['productivity', 'note', 'writing'],
            'data': ['data', 'analysis', 'database'],
            'ai': ['ai', 'llm', 'machine-learning'],
            'utility': ['utility', 'tool', 'helper']
        }

        # Find matching category
        for category, keywords in category_map.items():
            for tag in tags:
                if any(keyword in tag.lower() for keyword in keywords):
                    return category

        # Default category
        return 'other'


# Singleton instance
clawhub_sync_service = ClawHubSyncService()
