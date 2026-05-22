from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_ai_native_app_manifest import hasn_ai_native_app_manifest_dao
from backend.app.hasn.model import HasnAiNativeAppManifest
from backend.app.hasn.service.ai_native_builtin_manifests import COMMUNITY_AI_NATIVE_MANIFEST, KNOWLEDGE_AI_NATIVE_MANIFEST
from backend.app.hasn.service.workbench_app_registry import WorkbenchAppRegistry, workbench_app_registry
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone


class ManifestValidationResult:
    def __init__(self, *, valid: bool, errors: list[str], manifest_hash: str = '') -> None:
        self.valid = valid
        self.errors = errors
        self.manifest_hash = manifest_hash


class AINativeAppRegistry:
    def __init__(self, *, workbench_registry: WorkbenchAppRegistry | None = None) -> None:
        self.workbench_registry = workbench_registry or workbench_app_registry
        self._builtin_manifests = {
            'knowledge': KNOWLEDGE_AI_NATIVE_MANIFEST,
            'community': COMMUNITY_AI_NATIVE_MANIFEST,
        }

    def list_builtin_apps(self) -> list[dict[str, Any]]:
        return list(self._builtin_manifests.values())

    def get_builtin_manifest(self, app_id: str) -> dict[str, Any]:
        try:
            return self._builtin_manifests[app_id]
        except KeyError as exc:
            raise errors.NotFoundError(msg='AI-Native 应用不存在') from exc

    def validate_manifest(self, manifest: dict[str, Any]) -> ManifestValidationResult:
        errors_list: list[str] = []
        app_id = str(manifest.get('app_id') or '')
        version = str(manifest.get('version') or '')
        workspace_scope = list(manifest.get('workspace_scope') or [])
        collaboration_mode = str(manifest.get('collaboration_mode') or 'none')

        if not app_id:
            errors_list.append('app_id_required')
        if not version:
            errors_list.append('version_required')

        try:
            workbench_app = self.workbench_registry.get(app_id)
        except KeyError:
            errors_list.append('workbench_app_not_found')
            workbench_app = None

        if workbench_app is not None:
            if any(scope not in workbench_app.scope for scope in workspace_scope):
                errors_list.append('workspace_scope_exceeds_workbench_scope')
            if collaboration_mode != workbench_app.collaboration_mode:
                errors_list.append('collaboration_mode_mismatch')

        manifest_hash = _manifest_hash(manifest)
        return ManifestValidationResult(valid=not errors_list, errors=errors_list, manifest_hash=manifest_hash)

    async def publish_builtin(self, db: AsyncSession | None, app_id: str) -> dict[str, Any]:
        manifest = self.get_builtin_manifest(app_id)
        validation = self.validate_manifest(manifest)
        if not validation.valid:
            raise errors.RequestError(msg='manifest_validation_failed', data={'errors': validation.errors})
        row = HasnAiNativeAppManifest(
            app_id=manifest['app_id'],
            version=manifest['version'],
            status='published',
            workspace_scope=list(manifest.get('workspace_scope') or []),
            collaboration_mode=str(manifest.get('collaboration_mode') or 'none'),
            manifest_json=manifest,
            manifest_hash=validation.manifest_hash,
            published_at=timezone.now(),
        )
        if db is not None:
            db.add(row)
            await db.flush()
            return _manifest_payload(row)
        return _builtin_manifest_payload(manifest, manifest_hash=validation.manifest_hash)

    async def ensure_builtin_published(self, db: AsyncSession, app_id: str) -> dict[str, Any]:
        published = await self.get_published_manifest(db, app_id=app_id)
        if published:
            return published
        return await self.publish_builtin(db, app_id)

    async def get_published_manifest(self, db: AsyncSession, *, app_id: str) -> dict[str, Any] | None:
        stmt = await hasn_ai_native_app_manifest_dao.get_select()
        stmt = stmt.where(
            HasnAiNativeAppManifest.app_id == app_id,
            HasnAiNativeAppManifest.status == 'published',
        )
        row = (await db.execute(stmt)).scalars().first()
        if row is None:
            return None
        return _manifest_payload(row)

    async def list_manifests(self, db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_ai_native_app_manifest_dao.get_select())

    async def list_published_manifests(self, db: AsyncSession) -> list[dict[str, Any]]:
        stmt = await hasn_ai_native_app_manifest_dao.get_select()
        stmt = stmt.where(HasnAiNativeAppManifest.status == 'published')
        rows = (await db.execute(stmt)).scalars().all()
        manifests = {row.app_id: _manifest_payload(row) for row in rows}
        for app_id, manifest in self._builtin_manifests.items():
            manifests.setdefault(app_id, _builtin_manifest_payload(manifest))
        return list(manifests.values())

    async def get(self, db: AsyncSession, app_id: str) -> dict[str, Any]:
        published = await self.get_published_manifest(db, app_id=app_id)
        if published:
            return published
        if app_id in self._builtin_manifests:
            return _builtin_manifest_payload(self._builtin_manifests[app_id])
        raise errors.NotFoundError(msg='AI-Native 应用不存在')


def _manifest_payload(row: HasnAiNativeAppManifest | dict[str, Any]) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    return {
        'id': row.id,
        'app_id': row.app_id,
        'version': row.version,
        'status': row.status,
        'workspace_scope': row.workspace_scope,
        'collaboration_mode': row.collaboration_mode,
        'manifest_json': row.manifest_json,
        'manifest_hash': row.manifest_hash,
        'published_at': row.published_at,
    }


def _builtin_manifest_payload(manifest: dict[str, Any], *, manifest_hash: str | None = None) -> dict[str, Any]:
    return {
        'id': None,
        'app_id': manifest['app_id'],
        'version': manifest['version'],
        'status': 'published',
        'workspace_scope': list(manifest.get('workspace_scope') or []),
        'collaboration_mode': str(manifest.get('collaboration_mode') or 'none'),
        'manifest_json': manifest,
        'manifest_hash': manifest_hash or _manifest_hash(manifest),
        'published_at': timezone.now(),
    }


def _manifest_hash(manifest: dict[str, Any]) -> str:
    payload = repr(manifest).encode('utf-8')
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


ai_native_app_registry: AINativeAppRegistry = AINativeAppRegistry()
