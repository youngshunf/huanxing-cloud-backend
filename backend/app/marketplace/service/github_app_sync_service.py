"""
GitHub App Sync Service for Marketplace

Syncs app templates from huanxing-hub GitHub repository to database.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from git import Repo
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_app import marketplace_app_dao
from backend.app.marketplace.crud.crud_marketplace_app_version import marketplace_app_version_dao
from backend.app.marketplace.crud.crud_marketplace_sync_log import marketplace_sync_log_dao
from backend.app.marketplace.service.app_package_service import app_package_service
from backend.common.log import log
from backend.core.conf import settings
from backend.plugin.s3.crud.storage import s3_storage_dao
from backend.plugin.s3.utils.file_ops import build_object_url, write_bytes


class GitHubAppSyncService:
    """GitHub sync service for marketplace app templates"""

    def __init__(self):
        self.repo_url = getattr(settings, 'HUANXING_HUB_REPO_URL', 'https://github.com/youngshunf/huanxing-hub.git')
        self.local_path = getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub')
        self.repo: Repo | None = None

    async def sync_from_github(self, db: AsyncSession, force: bool = False) -> dict[str, Any]:
        """
        Sync app templates from GitHub repository

        Args:
            db: Database session
            force: Force full sync (ignore last sync time)

        Returns:
            Sync result with statistics
        """
        sync_log_id = None
        try:
            # Create sync log
            sync_log = await marketplace_sync_log_dao.create(db, {
                'sync_type': 'github',
                'resource_type': 'app',
                'status': 'in_progress',
                'started_at': datetime.now()
            })
            sync_log_id = sync_log.id

            # Clone or pull repository
            old_commit = await self._update_repository()

            # Get new commit
            new_commit = self.repo.head.commit.hexsha if self.repo else None

            # Scan for app templates
            apps_data = await self._scan_apps()

            # Sync to database
            synced_count = 0
            failed_count = 0
            errors = []

            for app_data in apps_data:
                try:
                    await self._sync_app(db, app_data)
                    synced_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"{app_data.get('app_id', 'unknown')}: {str(e)}")
                    log.error(f"Failed to sync app {app_data.get('app_id')}: {e}")

            # Update sync log
            await marketplace_sync_log_dao.update(db, sync_log_id, {
                'status': 'success' if failed_count == 0 else 'partial',
                'items_synced': synced_count,
                'items_failed': failed_count,
                'error_message': '\n'.join(errors) if errors else None,
                'git_commit_before': old_commit,
                'git_commit_after': new_commit,
                'completed_at': datetime.now()
            })

            return {
                'success': True,
                'synced': synced_count,
                'failed': failed_count,
                'errors': errors
            }

        except Exception as e:
            log.error(f"GitHub app sync failed: {e}")

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

    async def _update_repository(self) -> str | None:
        """
        Clone or pull the GitHub repository

        Returns:
            Old commit hash before update
        """
        old_commit = None

        if os.path.exists(self.local_path):
            # Pull latest changes
            log.info(f"Pulling latest changes from {self.repo_url}")
            self.repo = Repo(self.local_path)
            old_commit = self.repo.head.commit.hexsha
            origin = self.repo.remotes.origin
            origin.pull()
        else:
            # Clone repository
            log.info(f"Cloning repository from {self.repo_url}")
            self.repo = Repo.clone_from(self.repo_url, self.local_path)

        return old_commit

    async def _scan_apps(self) -> list[dict[str, Any]]:
        """
        Scan repository for app templates

        Returns:
            List of app metadata
        """
        apps = []
        templates_dir = Path(self.local_path) / 'templates'

        if not templates_dir.exists():
            log.warning(f"Templates directory not found: {templates_dir}")
            return apps

        # Scan all subdirectories for template.yaml
        for app_dir in templates_dir.iterdir():
            if not app_dir.is_dir():
                continue

            # Skip special directories
            if app_dir.name.startswith('_'):
                continue

            # Check for template.yaml
            template_yaml = app_dir / 'template.yaml'

            if template_yaml.exists():
                try:
                    app_data = await self._parse_template_yaml(template_yaml, app_dir.name)
                    apps.append(app_data)
                except Exception as e:
                    log.error(f"Failed to parse {template_yaml}: {e}")

        return apps

    async def _parse_template_yaml(self, template_path: Path, app_slug: str) -> dict[str, Any]:
        """
        Parse template.yaml file

        Args:
            template_path: Path to template.yaml
            app_slug: App slug (directory name)

        Returns:
            App metadata
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Get git commit hash
        commit_hash = self.repo.head.commit.hexsha if self.repo else None

        # Extract fields from template
        app_id = data.get('id', app_slug)
        name = data.get('name', app_slug)
        display_name = data.get('display_name', name)
        description = data.get('description', '')
        version = data.get('version', '1.0.0')
        emoji = data.get('emoji', '')

        # Handle icon
        icon_s3_url = data.get('icon_s3_url', '')

        # Check if we need to upload local icon to S3
        if not icon_s3_url:
            app_dir = template_path.parent
            icon_s3_url = await self._upload_icon_to_cdn(app_dir, app_id)

            # Update template.yaml with S3 URL
            if icon_s3_url:
                data['icon_s3_url'] = icon_s3_url
                await self._update_template_yaml(template_path, data)

        # Handle tags
        tags = data.get('tags', [])
        tags_str = ','.join(tags) if isinstance(tags, list) else str(tags)

        # Handle skills dependencies
        skills = data.get('skills', [])
        skill_dependencies = ','.join(skills) if isinstance(skills, list) else str(skills)

        # Handle SOPs dependencies
        sops = data.get('sops', [])
        sop_dependencies = ','.join(sops) if isinstance(sops, list) else str(sops)

        # Handle pricing
        pricing = data.get('pricing', {})
        pricing_tier = pricing.get('tier', 'free')

        # Build app data
        app_data = {
            'app_id': app_id,
            'name': name,
            'description': description,
            'icon_url': icon_s3_url,
            'emoji': emoji,
            'author_name': 'huanxing',
            'category': 'assistant',  # TODO: extract from directory structure or metadata
            'tags': tags_str,
            'pricing_type': pricing_tier,
            'price': 0,
            'is_private': False,
            'is_official': True,
            'skill_dependencies': skill_dependencies,
            'sop_dependencies': sop_dependencies,
            'repo_path': f"templates/{app_slug}",
            'git_commit_hash': commit_hash,
            'version': version,
            'synced_at': datetime.now()
        }

        return app_data

    async def _upload_icon_to_cdn(self, app_dir: Path, app_id: str) -> str | None:
        """
        Upload local icon to S3 storage

        Args:
            app_dir: App directory path
            app_id: App ID

        Returns:
            S3 URL or None if no icon found
        """
        # Check for icon files
        for icon_name in ['icon.png', 'icon.svg', 'icon.jpg', 'icon.jpeg']:
            icon_path = app_dir / icon_name
            if icon_path.exists():
                try:
                    log.info(f"Uploading icon to S3: {icon_path}")

                    # Read icon file
                    with open(icon_path, 'rb') as f:
                        icon_content = f.read()

                    # Get default S3 storage (assuming first storage is default)
                    # TODO: Make this configurable via settings
                    from sqlalchemy.ext.asyncio import AsyncSession
                    from backend.database.db import async_db_session

                    async with async_db_session() as db:
                        s3_storages = await s3_storage_dao.get_all(db)
                        if not s3_storages:
                            log.error("No S3 storage configured")
                            return None

                        s3_storage = s3_storages[0]

                        # Generate S3 path: marketplace/apps/{app_id}/icon.{ext}
                        ext = icon_path.suffix
                        s3_path = f"marketplace/apps/{app_id}/icon{ext}"

                        # Determine content type
                        content_type = None
                        if ext == '.svg':
                            content_type = 'image/svg+xml'
                        elif ext in ['.png', '.jpg', '.jpeg']:
                            content_type = f'image/{ext[1:]}'

                        # Upload to S3
                        await write_bytes(s3_storage, s3_path, icon_content, content_type)

                        # Build public URL
                        s3_url = build_object_url(s3_storage, s3_path)

                    log.info(f"Icon uploaded to S3: {s3_url}")
                    return s3_url

                except Exception as e:
                    log.error(f"Failed to upload icon to S3: {e}")
                    return None

        log.warning(f"No icon found for app {app_id}")
        return None

    async def _update_template_yaml(self, template_path: Path, data: dict):
        """
        Update template.yaml with new data (e.g., icon_cdn_url)

        Args:
            template_path: Path to template.yaml
            data: Updated data
        """
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)

            log.info(f"Updated template.yaml: {template_path}")

        except Exception as e:
            log.error(f"Failed to update template.yaml: {e}")

    async def _sync_app(self, db: AsyncSession, app_data: dict[str, Any]):
        """
        Sync single app to database

        Args:
            db: Database session
            app_data: App metadata
        """
        app_id = app_data['app_id']
        version = app_data.pop('version')

        # Check if app exists
        existing_app = await marketplace_app_dao.get_by_id(db, app_id)

        if existing_app:
            # Update existing app
            await marketplace_app_dao.update(db, existing_app.id, app_data)
            log.info(f"Updated app: {app_id}")
        else:
            # Create new app
            await marketplace_app_dao.create(db, app_data)
            log.info(f"Created app: {app_id}")

        # Build package
        package_info = await app_package_service.build_app_package(app_id, version)

        # Create or update version
        existing_version = await marketplace_app_version_dao.get_by_app_and_version(db, app_id, version)

        version_data = {
            'app_id': app_id,
            'version': version,
            'git_commit_hash': app_data['git_commit_hash'],
            'package_path': package_info['package_path'],
            'file_hash': package_info['file_hash'],
            'file_size': package_info['file_size'],
            'is_latest': True,
            'published_at': datetime.now()
        }

        if existing_version:
            await marketplace_app_version_dao.update(db, existing_version.id, version_data)
            log.info(f"Updated app version: {app_id} v{version}")
        else:
            # Mark all other versions as not latest
            await marketplace_app_version_dao.mark_all_not_latest(db, app_id)

            # Create new version
            await marketplace_app_version_dao.create(db, version_data)
            log.info(f"Created app version: {app_id} v{version}")


# Global instance
github_app_sync_service = GitHubAppSyncService()
