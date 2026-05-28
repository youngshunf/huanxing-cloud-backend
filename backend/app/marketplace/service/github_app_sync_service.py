"""GitHub sync service for marketplace templates."""
from __future__ import annotations

import os

from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from git import Repo

from backend.app.marketplace.crud.crud_marketplace_sync_log import marketplace_sync_log_dao
from backend.app.marketplace.crud.crud_marketplace_template import marketplace_template_dao
from backend.app.marketplace.crud.crud_marketplace_template_version import marketplace_template_version_dao
from backend.app.marketplace.schema.marketplace_sync_log import (
    CreateMarketplaceSyncLogParam,
    UpdateMarketplaceSyncLogParam,
)
from backend.app.marketplace.schema.marketplace_template import (
    CreateMarketplaceTemplateParam,
    UpdateMarketplaceTemplateParam,
)
from backend.app.marketplace.schema.marketplace_template_version import (
    CreateMarketplaceTemplateVersionParam,
    UpdateMarketplaceTemplateVersionParam,
)
from backend.app.marketplace.service.app_package_service import app_package_service
from backend.app.marketplace.service.package_validation import normalize_tags
from backend.app.marketplace.storage.s3_storage import marketplace_storage_service
from backend.common.log import log
from backend.core.conf import settings
from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class GitHubAppSyncService:
    """Sync huanxing-hub templates into marketplace_template."""

    def __init__(self) -> None:
        self.repo_url = getattr(settings, 'HUANXING_HUB_REPO_URL', 'https://github.com/youngshunf/huanxing-hub.git')
        self.local_path = getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub')
        self.repo: Repo | None = None

    async def sync_from_github(self, db: AsyncSession, force: bool = False) -> dict[str, Any]:  # noqa: FBT001, FBT002
        sync_log_id = None
        try:
            sync_log = await marketplace_sync_log_dao.create(
                db,
                CreateMarketplaceSyncLogParam(
                    sync_type='github',
                    status='in_progress',
                    started_at=timezone.now(),
                ),
            )
            await db.flush()
            sync_log_id = sync_log.id

            old_commit = await self._update_repository()
            new_commit = self.repo.head.commit.hexsha if self.repo else None
            templates_data = await self._scan_templates()

            synced_count = 0
            failed_count = 0
            errors = []
            for template_data in templates_data:
                try:
                    await self._sync_template(db, template_data)
                    synced_count += 1
                except Exception as exc:  # noqa: PERF203
                    failed_count += 1
                    errors.append(f"{template_data.get('template_id', 'unknown')}: {exc}")
                    log.error(f"Failed to sync template {template_data.get('template_id')}: {exc}")

            await marketplace_sync_log_dao.update(
                db,
                sync_log_id,
                UpdateMarketplaceSyncLogParam(
                    status='success' if failed_count == 0 else 'partial',
                    items_synced=synced_count,
                    items_failed=failed_count,
                    error_message='\n'.join(errors) if errors else None,
                    git_commit_before=old_commit,
                    git_commit_after=new_commit,
                    completed_at=timezone.now(),
                ),
            )

            return {'success': True, 'synced': synced_count, 'failed': failed_count, 'errors': errors}  # noqa: TRY300
        except Exception as exc:
            log.error(f"GitHub template sync failed: {exc}")
            if sync_log_id:
                await marketplace_sync_log_dao.update(
                    db,
                    sync_log_id,
                    UpdateMarketplaceSyncLogParam(
                        status='failed',
                        error_message=str(exc),
                        completed_at=timezone.now(),
                    ),
                )
            return {'success': False, 'error': str(exc)}

    async def _update_repository(self) -> str | None:
        old_commit = None
        if os.path.exists(self.local_path):  # noqa: ASYNC240
            self.repo = Repo(self.local_path)
            old_commit = self.repo.head.commit.hexsha
            self.repo.remotes.origin.pull()
        else:
            self.repo = Repo.clone_from(self.repo_url, self.local_path)
        return old_commit

    async def _scan_templates(self) -> list[dict[str, Any]]:
        templates = []
        templates_root = Path(self.local_path) / 'templates'
        if not templates_root.exists():
            log.warning(f"Templates directory not found: {templates_root}")
            return templates

        for template_yaml in templates_root.glob('*/*/template.yaml'):
            try:
                templates.append(await self._parse_template_yaml(template_yaml))
            except Exception as exc:  # noqa: PERF203
                log.error(f"Failed to parse {template_yaml}: {exc}")
        return templates

    async def _parse_template_yaml(self, template_path: Path) -> dict[str, Any]:
        relative = template_path.parent.relative_to(Path(self.local_path))
        parts = relative.parts
        if len(parts) != 3 or parts[0] != 'templates':
            raise ValueError(f"Unexpected template path: {relative}")

        _, category, slug = parts
        data = yaml.safe_load(template_path.read_text(encoding='utf-8')) or {}  # noqa: ASYNC240
        if not isinstance(data, dict):
            raise TypeError(f"template.yaml must be a mapping: {template_path}")

        display_name = data.get('display_name') or data.get('name') or slug
        description = data.get('description') or ''
        version = str(data.get('version') or '1.0.0')
        namespace = f'huanxing/{category}'
        template_id = f'{namespace}/{slug}'
        skill_deps = data.get('skills') or data.get('skill_dependencies') or []
        sop_deps = data.get('sops') or data.get('sop_dependencies') or []
        tags = normalize_tags(data.get('tags'))
        icon_path = self._find_local_icon(template_path.parent)

        return {
            'template_id': template_id,
            'namespace': namespace,
            'slug': slug,
            'template_type': data.get('template_type') or 'agent_template',
            'name': str(display_name),
            'name_en': str(display_name),
            'name_zh': str(display_name),
            'description': str(description),
            'description_en': str(description),
            'description_zh': str(description),
            'source_language': 'zh' if any(ord(c) > 127 for c in str(display_name)) else 'en',
            'icon_url': data.get('icon_url') or data.get('icon_s3_url') or data.get('icon_cdn_url'),
            'icon_path': icon_path,
            'emoji': data.get('emoji'),
            'author_name': data.get('author') or 'huanxing',
            'pricing_type': (data.get('pricing') or {}).get('tier', data.get('pricing_type', 'free')),
            'price': (data.get('pricing') or {}).get('price', data.get('price', 0)),
            'is_private': False,
            'is_official': True,
            'download_count': 0,
            'category': data.get('category') or category,
            'tags': ','.join(tags),
            'source_type': 'official',
            'source_repo_path': f'templates/{category}/{slug}',
            'skill_dependencies': ','.join(skill_deps) if isinstance(skill_deps, list) else str(skill_deps),
            'sop_dependencies': ','.join(sop_deps) if isinstance(sop_deps, list) else str(sop_deps),
            'repo_path': f'templates/{category}/{slug}',
            'git_commit_hash': self.repo.head.commit.hexsha if self.repo else None,
            'synced_at': timezone.now(),
            'translated_at': timezone.now(),
            'status': 'published',
            'visibility': 'public',
            'version': version,
            'skill_dependencies_versioned': dict.fromkeys(skill_deps, '*') if isinstance(skill_deps, list) else None,
        }

    @staticmethod
    def _find_local_icon(template_dir: Path) -> Path | None:
        for icon_name in ('icon.svg', 'icon.png', 'icon.jpg', 'icon.jpeg'):
            icon_path = template_dir / icon_name
            if icon_path.exists():
                return icon_path
        return None

    async def _sync_template(self, db: AsyncSession, template_data: dict[str, Any]) -> None:
        template_id = template_data['template_id']
        version = template_data.pop('version')
        icon_path = template_data.pop('icon_path', None)
        skill_dependencies_versioned = template_data.pop('skill_dependencies_versioned', None)

        if icon_path and not template_data.get('icon_url'):
            template_data['icon_url'] = await marketplace_storage_service.upload_icon(
                db=db,
                item_type='template',
                item_id=template_id,
                content=Path(icon_path).read_bytes(),  # noqa: ASYNC240
                filename=Path(icon_path).name,
            )

        existing_template = await marketplace_template_dao.get_by_id(db, template_id)
        if existing_template:
            await marketplace_template_dao.update(
                db,
                existing_template.id,
                UpdateMarketplaceTemplateParam(**template_data),
            )
        else:
            await marketplace_template_dao.create(db, CreateMarketplaceTemplateParam(**template_data))

        package_info = await app_package_service.build_template_package(template_id, version)
        existing_version = await marketplace_template_version_dao.get_by_template_and_version(db, template_id, version)
        version_data = {
            'template_id': template_id,
            'version': version,
            'changelog': f'Version {version}',
            'skill_dependencies_versioned': skill_dependencies_versioned,
            'package_url': package_info['package_path'],
            'file_hash': package_info['file_hash'],
            'file_size': package_info['file_size'],
            'is_latest': True,
            'published_at': timezone.now(),
        }
        if existing_version:
            await marketplace_template_version_dao.update(
                db,
                existing_version.id,
                UpdateMarketplaceTemplateVersionParam(**version_data),
            )
        else:
            await marketplace_template_version_dao.mark_all_not_latest(db, template_id)
            await marketplace_template_version_dao.create(db, CreateMarketplaceTemplateVersionParam(**version_data))


github_app_sync_service = GitHubAppSyncService()
