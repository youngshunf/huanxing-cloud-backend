"""
GitHub Sync Service for Marketplace Skills

Syncs skills from huanxing-hub GitHub repository to database.
"""
import json
import os

from pathlib import Path
from typing import Any

import yaml

from git import Repo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao
from backend.app.marketplace.crud.crud_marketplace_skill_version import marketplace_skill_version_dao
from backend.app.marketplace.crud.crud_marketplace_sync_log import marketplace_sync_log_dao
from backend.app.marketplace.schema.marketplace_skill import CreateMarketplaceSkillParam, UpdateMarketplaceSkillParam
from backend.app.marketplace.schema.marketplace_skill_version import (
    CreateMarketplaceSkillVersionParam,
    UpdateMarketplaceSkillVersionParam,
)
from backend.app.marketplace.schema.marketplace_sync_log import (
    CreateMarketplaceSyncLogParam,
    UpdateMarketplaceSyncLogParam,
)
from backend.app.marketplace.service.package_validation import normalize_tags
from backend.app.marketplace.service.translation_service import translation_service
from backend.app.marketplace.storage.s3_storage import marketplace_storage_service
from backend.common.log import log
from backend.core.conf import settings
from backend.utils.timezone import timezone


class GitHubSyncService:
    """GitHub sync service for marketplace skills"""

    def __init__(self) -> None:
        self.repo_url = getattr(settings, 'HUANXING_HUB_REPO_URL', 'https://github.com/youngshunf/huanxing-hub.git')
        self.local_path = getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub')
        self.repo: Repo | None = None

    async def sync_from_github(self, db: AsyncSession, force: bool = False) -> dict[str, Any]:  # noqa: FBT001, FBT002
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
            sync_log = await marketplace_sync_log_dao.create(
                db,
                CreateMarketplaceSyncLogParam(
                    sync_type='github',
                    status='in_progress',
                    started_at=timezone.now(),
                ),
            )
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
                except Exception as e:  # noqa: PERF203
                    failed_count += 1
                    errors.append(f"{skill_data.get('skill_id', 'unknown')}: {e!s}")
                    log.error(f"Failed to sync skill {skill_data.get('skill_id')}: {e}")

            # Update sync log
            if sync_log_id:
                await marketplace_sync_log_dao.update(
                    db,
                    sync_log_id,
                    UpdateMarketplaceSyncLogParam(
                        status='success' if failed_count == 0 else 'partial',
                        items_synced=synced_count,
                        items_failed=failed_count,
                        error_message='\n'.join(errors) if errors else None,
                        completed_at=timezone.now(),
                    ),
                )
                await db.commit()

            return {  # noqa: TRY300
                'success': True,
                'synced': synced_count,
                'failed': failed_count,
                'errors': errors,
            }

        except Exception as e:
            log.error(f"GitHub sync failed: {e}")

            # Update sync log
            if sync_log_id:
                await marketplace_sync_log_dao.update(
                    db,
                    sync_log_id,
                    UpdateMarketplaceSyncLogParam(
                        status='failed',
                        error_message=str(e),
                        completed_at=timezone.now(),
                    ),
                )
                await db.commit()

            return {
                'success': False,
                'error': str(e),
            }

    async def _update_repository(self) -> None:
        """Clone or pull the GitHub repository"""
        if os.path.exists(self.local_path):  # noqa: ASYNC240
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
        repo_root = Path(self.local_path)
        scan_roots = (
            ('huanxing-skills', 'official'),
            ('clawhub', 'clawhub'),
            ('github', 'github'),
        )

        for root_name, source_type in scan_roots:
            root = repo_root / root_name
            if not root.exists():
                continue
            for skill_md in root.glob('*/*/SKILL.md'):
                try:
                    skills.append(await self._parse_skill_markdown(skill_md, root_name, source_type))
                except Exception as exc:  # noqa: PERF203
                    log.error(f"Failed to parse {skill_md}: {exc}")

        if not skills:
            log.warning(f"No SKILL.md skills found under {repo_root}")

        return skills

    async def _parse_skill_markdown(self, skill_md_path: Path, root_name: str, source_type: str) -> dict[str, Any]:
        relative = skill_md_path.parent.relative_to(Path(self.local_path))
        parts = relative.parts
        if len(parts) != 3:
            raise ValueError(f"Unexpected skill path: {relative}")

        _, owner_or_category, slug = parts
        if root_name == 'huanxing-skills':
            namespace = f'huanxing/{owner_or_category}'
            repo_path = f'huanxing-skills/{owner_or_category}/{slug}'
            category = owner_or_category
            is_official = True
        elif root_name == 'clawhub':
            namespace = f'clawhub/{owner_or_category}'
            repo_path = f'clawhub/{owner_or_category}/{slug}'
            category = None
            is_official = False
        elif root_name == 'github':
            namespace = f'github/{owner_or_category}'
            repo_path = f'github/{owner_or_category}/{slug}'
            category = None
            is_official = False
        else:
            raise ValueError(f"Unsupported skill root: {root_name}")

        text = skill_md_path.read_text(encoding='utf-8')  # noqa: ASYNC240
        metadata = self._extract_skill_frontmatter(text)
        for field in ('name', 'description'):
            if not metadata.get(field):
                raise ValueError(f"SKILL.md frontmatter missing {field}: {skill_md_path}")

        tags = normalize_tags(metadata.get('tags'))
        icon_path = self._find_local_icon(skill_md_path.parent)
        skill_id = f'{namespace}/{slug}'
        return {
            'skill_id': skill_id,
            'namespace': namespace,
            'slug': slug,
            'category': metadata.get('category') or category,
            'repo_path': repo_path,
            'git_commit_hash': self.repo.head.commit.hexsha if self.repo else None,
            'icon_url': metadata.get('icon_url') or metadata.get('icon_s3_url') or metadata.get('icon_cdn_url'),
            'icon_path': icon_path,
            'emoji': metadata.get('emoji'),
            'author_name': metadata.get('author') or metadata.get('author_name'),
            'tags': json.dumps(tags, ensure_ascii=False),
            'pricing_type': metadata.get('pricing_type', 'free'),
            'price': metadata.get('price', 0),
            'is_official': is_official,
            'is_private': False,
            'source_type': source_type,
            'source_language': 'zh' if any(ord(c) > 127 for c in str(metadata.get('name'))) else 'en',
            'name': metadata.get('name'),
            'description': metadata.get('description'),
            'version': str(metadata.get('version') or '1.0.0'),
            'changelog': metadata.get('changelog') or f"Version {metadata.get('version') or '1.0.0'}",
            'versions': [{
                'version': str(metadata.get('version') or '1.0.0'),
                'changelog': metadata.get('changelog') or f"Version {metadata.get('version') or '1.0.0'}",
                'package_url': metadata.get('package_url'),
                'file_hash': metadata.get('file_hash'),
                'file_size': metadata.get('file_size'),
                'is_latest': True,
            }],
        }

    @staticmethod
    def _extract_skill_frontmatter(markdown: str) -> dict[str, Any]:
        import re

        match = re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|\Z)', markdown, re.DOTALL)
        if not match:
            raise ValueError('SKILL.md missing YAML frontmatter')
        data = yaml.safe_load(match.group(1)) or {}
        if not isinstance(data, dict):
            raise TypeError('SKILL.md frontmatter must be a mapping')
        return data

    @staticmethod
    def _find_local_icon(skill_dir: Path) -> Path | None:
        for icon_name in ('icon.svg', 'icon.png', 'icon.jpg', 'icon.jpeg'):
            icon_path = skill_dir / icon_name
            if icon_path.exists():
                return icon_path
        return None

    async def _sync_skill(self, db: AsyncSession, skill_data: dict[str, Any]) -> None:
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
            'namespace': skill_data.get('namespace'),
            'slug': skill_data.get('slug'),
            'name': name,
            'name_en': translated.get('name_en'),
            'name_zh': translated.get('name_zh'),
            'description_en': translated.get('description_en'),
            'description_zh': translated.get('description_zh'),
            'source_language': translated.get('source_language', skill_data.get('source_language')),
            'icon_url': await self._resolve_icon_url(db, skill_data),
            'emoji': skill_data.get('emoji'),
            'author_name': skill_data.get('author_name'),
            'category': skill_data.get('category'),
            'tags': skill_data.get('tags'),
            'pricing_type': skill_data.get('pricing_type'),
            'price': skill_data.get('price'),
            'is_official': skill_data.get('is_official'),
            'is_private': skill_data.get('is_private', False),
            'status': 'published',
            'visibility': 'public',
            'source_type': skill_data.get('source_type'),
            'download_count': skill_data.get('download_count', 0),
            'repo_path': skill_data.get('repo_path'),
            'git_commit_hash': skill_data.get('git_commit_hash'),
            'synced_at': timezone.now(),
            'translated_at': timezone.now(),
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

    async def _resolve_icon_url(self, db: AsyncSession, skill_data: dict[str, Any]) -> str | None:
        icon_url = skill_data.get('icon_url')
        icon_path = skill_data.get('icon_path')
        if icon_url or not icon_path:
            return icon_url
        try:
            return await marketplace_storage_service.upload_icon(
                db=db,
                item_type='skill',
                item_id=skill_data['skill_id'],
                content=Path(icon_path).read_bytes(),  # noqa: ASYNC240
                filename=Path(icon_path).name,
            )
        except Exception as exc:
            log.error(f"Failed to upload skill icon {icon_path}: {exc}")
            return None

    async def _sync_skill_version(
        self,
        db: AsyncSession,
        db_skill_id: int,
        skill_id: str,
        version_data: dict[str, Any],
    ) -> None:
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
            db, skill_id, version
        )

        # Prepare version record
        version_record = {
            'skill_id': skill_id,
            'version': version,
            'changelog': version_data.get('changelog'),
            'package_url': version_data.get('package_url'),
            'file_hash': version_data.get('file_hash'),
            'file_size': version_data.get('file_size'),
            'is_latest': version_data.get('is_latest', True),
        }

        if existing_version:
            # Update existing version
            await marketplace_skill_version_dao.update(
                db,
                existing_version.id,
                UpdateMarketplaceSkillVersionParam(**version_record),
            )
        else:
            # Create new version
            await marketplace_skill_version_dao.create(db, CreateMarketplaceSkillVersionParam(**version_record))


# Singleton instance
github_sync_service = GitHubSyncService()
