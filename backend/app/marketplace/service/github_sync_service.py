"""
GitHub Sync Service for Marketplace Skills

Syncs skills from huanxing-hub GitHub repository to database.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from git import Repo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao
from backend.app.marketplace.crud.crud_marketplace_skill_version import marketplace_skill_version_dao
from backend.app.marketplace.crud.crud_marketplace_sync_log import marketplace_sync_log_dao
from backend.app.marketplace.schema.marketplace_skill import CreateMarketplaceSkillParam, UpdateMarketplaceSkillParam
from backend.app.marketplace.schema.marketplace_skill_version import CreateMarketplaceSkillVersionParam, UpdateMarketplaceSkillVersionParam
from backend.app.marketplace.schema.marketplace_sync_log import CreateMarketplaceSyncLogParam, UpdateMarketplaceSyncLogParam
from backend.app.marketplace.service.translation_service import translation_service
from backend.common.log import log
from backend.core.conf import settings


class GitHubSyncService:
    """GitHub sync service for marketplace skills"""

    def __init__(self):
        self.repo_url = getattr(settings, 'HUANXING_HUB_REPO_URL', 'https://github.com/youngshunf/huanxing-hub.git')
        self.local_path = getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub')
        self.repo: Repo | None = None

    async def sync_from_github(self, db: AsyncSession, force: bool = False) -> dict[str, Any]:
        """
        Sync skills from GitHub repository

        Args:
            db: Database session
            force: Force full sync (ignore last sync time)

        Returns:
            Sync result with statistics
        """
        sync_log_id = None
        try:
            # Create sync log
            sync_log = await marketplace_sync_log_dao.create(db, CreateMarketplaceSyncLogParam(
                sync_type='github',
                status='in_progress',
                started_at=datetime.now()
            ))
            await db.flush()
            sync_log_id = sync_log.id if sync_log else None

            # Clone or pull repository
            await self._update_repository()

            # Scan for skills
            skills_data = await self._scan_skills()

            # Sync to database
            synced_count = 0
            failed_count = 0
            errors = []

            for skill_data in skills_data:
                try:
                    await self._sync_skill(db, skill_data)
                    synced_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"{skill_data.get('skill_id', 'unknown')}: {str(e)}")
                    log.error(f"Failed to sync skill {skill_data.get('skill_id')}: {e}")

            # Update sync log
            if sync_log_id:
                await marketplace_sync_log_dao.update(db, sync_log_id, UpdateMarketplaceSyncLogParam(
                    status='success' if failed_count == 0 else 'partial',
                    items_synced=synced_count,
                    items_failed=failed_count,
                    error_message='\n'.join(errors) if errors else None,
                    completed_at=datetime.now()
                ))
                await db.commit()

            return {
                'success': True,
                'synced': synced_count,
                'failed': failed_count,
                'errors': errors
            }

        except Exception as e:
            log.error(f"GitHub sync failed: {e}")

            # Update sync log
            if sync_log_id:
                await marketplace_sync_log_dao.update(db, sync_log_id, UpdateMarketplaceSyncLogParam(
                    status='failed',
                    error_message=str(e),
                    completed_at=datetime.now()
                ))
                await db.commit()

            return {
                'success': False,
                'error': str(e)
            }

    async def _update_repository(self):
        """Clone or pull the GitHub repository"""
        if os.path.exists(self.local_path):
            # Pull latest changes
            log.info(f"Pulling latest changes from {self.repo_url}")
            self.repo = Repo(self.local_path)
            origin = self.repo.remotes.origin
            origin.pull()
        else:
            # Clone repository
            log.info(f"Cloning repository from {self.repo_url}")
            self.repo = Repo.clone_from(self.repo_url, self.local_path)

    async def _scan_skills(self) -> list[dict[str, Any]]:
        """
        Scan repository for skills

        Returns:
            List of skill metadata
        """
        skills = []
        skills_dir = Path(self.local_path) / 'skills'

        if not skills_dir.exists():
            log.warning(f"Skills directory not found: {skills_dir}")
            return skills

        # Scan all subdirectories for manifest.yaml or skill.json
        for category_dir in skills_dir.iterdir():
            if not category_dir.is_dir():
                continue

            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue

                # Try manifest.yaml first (new format), then skill.json (legacy)
                manifest_yaml = skill_dir / 'manifest.yaml'
                skill_json = skill_dir / 'skill.json'

                if manifest_yaml.exists():
                    try:
                        skill_data = await self._parse_manifest_yaml(manifest_yaml, category_dir.name, skill_dir.name)
                        skills.append(skill_data)
                    except Exception as e:
                        log.error(f"Failed to parse {manifest_yaml}: {e}")
                elif skill_json.exists():
                    try:
                        skill_data = await self._parse_skill_json(skill_json, category_dir.name, skill_dir.name)
                        skills.append(skill_data)
                    except Exception as e:
                        log.error(f"Failed to parse {skill_json}: {e}")

        return skills

    async def _parse_manifest_yaml(self, manifest_path: Path, category: str, skill_slug: str) -> dict[str, Any]:
        """
        Parse manifest.yaml file (new format)

        Args:
            manifest_path: Path to manifest.yaml
            category: Category name
            skill_slug: Skill slug

        Returns:
            Skill metadata
        """
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Get git commit hash
        commit_hash = self.repo.head.commit.hexsha if self.repo else None

        # Extract fields from manifest
        skill_id = data.get('id', skill_slug)
        name = data.get('name', skill_slug)
        description = data.get('description', '')
        version = data.get('version', '1.0.0')
        author = data.get('author', 'unknown')

        # Handle security fields
        security = data.get('security', {})
        risk_level = security.get('risk_level', data.get('risk_level', 'low'))
        review_status = security.get('review_status', data.get('review_status', 'pending'))

        # Handle pricing
        pricing = data.get('pricing', {})
        pricing_tier = pricing.get('tier', data.get('pricing_type', 'free'))

        # Detect if official skill
        is_official = review_status == 'official' or author == 'huanxing'

        # Build skill data
        skill_data = {
            'skill_id': f"{category}/{skill_id}",
            'category': category,
            'repo_path': f"skills/{category}/{skill_slug}",
            'git_commit_hash': commit_hash,
            'icon_url': data.get('icon_cdn_url', data.get('icon')),
            'emoji': data.get('emoji'),
            'author_name': author,
            'tags': json.dumps(data.get('tags', [])),
            'pricing_type': pricing_tier,
            'price': pricing.get('price', 0),
            'is_official': is_official,
            'source': data.get('source', 'huanxing'),
            'source_language': 'zh' if any(ord(c) > 127 for c in name) else 'en',
            'name': name,
            'description': description,
            'version': version,
            'changelog': data.get('changelog', f'Version {version}'),
        }

        return skill_data

    async def _parse_skill_json(self, skill_json_path: Path, category: str, skill_slug: str) -> dict[str, Any]:
        """
        Parse skill.json file

        Args:
            skill_json_path: Path to skill.json
            category: Category name
            skill_slug: Skill slug

        Returns:
            Skill metadata
        """
        with open(skill_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Get git commit hash
        commit_hash = self.repo.head.commit.hexsha if self.repo else None

        # Build skill data
        skill_data = {
            'skill_id': f"{category}/{skill_slug}",
            'category': category,
            'repo_path': f"skills/{category}/{skill_slug}",
            'git_commit_hash': commit_hash,
            'icon_url': data.get('icon'),
            'emoji': data.get('emoji'),
            'author_name': data.get('author'),
            'tags': json.dumps(data.get('tags', [])),
            'pricing_type': data.get('pricing_type', 'free'),
            'price': data.get('price', 0),
            'is_official': data.get('is_official', False),
            'is_private': data.get('is_private', False),
        }

        # Handle i18n fields
        if 'i18n' in data:
            i18n = data['i18n']
            skill_data['name_en'] = i18n.get('en', {}).get('name')
            skill_data['name_zh'] = i18n.get('zh', {}).get('name')
            skill_data['description_en'] = i18n.get('en', {}).get('description')
            skill_data['description_zh'] = i18n.get('zh', {}).get('description')

            # Detect source language
            if skill_data['name_en'] and not skill_data['name_zh']:
                skill_data['source_language'] = 'en'
            elif skill_data['name_zh'] and not skill_data['name_en']:
                skill_data['source_language'] = 'zh'
        else:
            # Legacy format: single name/description
            name = data.get('name')
            description = data.get('description')

            if name or description:
                # Auto-translate
                translated = await translation_service.translate_skill_metadata(
                    name=name,
                    description=description
                )
                skill_data.update(translated)

        # Parse versions
        versions = data.get('versions', [])
        skill_data['versions'] = versions
        if versions:
            skill_data['latest_version'] = versions[0].get('version', '1.0.0')

        return skill_data

    async def _sync_skill(self, db: AsyncSession, skill_data: dict[str, Any]):
        """
        Sync a single skill to database

        Args:
            db: Database session
            skill_data: Skill metadata
        """
        skill_id = skill_data['skill_id']

        # Translate name and description
        name = skill_data.get('name', '')
        description = skill_data.get('description', '')

        translated = await translation_service.translate_skill_metadata(
            name=name,
            description=description
        )

        # Check if skill exists
        existing_skill = await marketplace_skill_dao.get_by_id(db, skill_id)

        # Prepare skill record
        skill_record = {
            'skill_id': skill_id,
            'name_en': translated.get('name_en'),
            'name_zh': translated.get('name_zh'),
            'description_en': translated.get('description_en'),
            'description_zh': translated.get('description_zh'),
            'source_language': translated.get('source_language', skill_data.get('source_language')),
            'icon_url': skill_data.get('icon_url'),
            'emoji': skill_data.get('emoji'),
            'author_name': skill_data.get('author_name'),
            'category': skill_data.get('category'),
            'tags': skill_data.get('tags'),
            'pricing_type': skill_data.get('pricing_type'),
            'price': skill_data.get('price'),
            'is_official': skill_data.get('is_official'),
            'is_private': skill_data.get('is_private', False),
            'download_count': skill_data.get('download_count', 0),
            'repo_path': skill_data.get('repo_path'),
            'git_commit_hash': skill_data.get('git_commit_hash'),
            'synced_at': datetime.now(),
            'translated_at': datetime.now()
        }

        if existing_skill:
            # Update existing skill
            await marketplace_skill_dao.update(db, existing_skill.id, UpdateMarketplaceSkillParam(**skill_record))
            db_skill_id = existing_skill.id
        else:
            # Create new skill
            await marketplace_skill_dao.create(db, CreateMarketplaceSkillParam(**skill_record))
            await db.flush()
            # Re-query to get the created skill
            new_skill = await marketplace_skill_dao.get_by_id(db, skill_id)
            db_skill_id = new_skill.id if new_skill else None

        # Sync versions
        versions = skill_data.get('versions', [])
        for version_data in versions:
            await self._sync_skill_version(db, db_skill_id, skill_id, version_data)

    async def _sync_skill_version(
        self,
        db: AsyncSession,
        db_skill_id: int,
        skill_id: str,
        version_data: dict[str, Any]
    ):
        """
        Sync a skill version

        Args:
            db: Database session
            db_skill_id: Database skill ID
            skill_id: Skill ID
            version_data: Version metadata
        """
        version = version_data.get('version', '1.0.0')

        # Check if version exists
        existing_version = await marketplace_skill_version_dao.get_by_skill_and_version(
            db, db_skill_id, version
        )

        # Prepare version record
        version_record = {
            'skill_id': skill_id,
            'version': version,
            'changelog': version_data.get('changelog'),
            'package_url': version_data.get('package_url'),
            'file_hash': version_data.get('file_hash'),
            'file_size': version_data.get('file_size'),
            'is_latest': version_data.get('is_latest', True)
        }

        if existing_version:
            # Update existing version
            await marketplace_skill_version_dao.update(db, existing_version.id, UpdateMarketplaceSkillVersionParam(**version_record))
        else:
            # Create new version
            await marketplace_skill_version_dao.create(db, CreateMarketplaceSkillVersionParam(**version_record))


# Singleton instance
github_sync_service = GitHubSyncService()
