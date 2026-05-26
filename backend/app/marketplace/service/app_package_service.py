"""
App Package Service for Marketplace

Handles packaging app templates into ZIP files for download.
"""
import hashlib
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from backend.common.log import log
from backend.core.conf import settings


class AppPackageService:
    """App package service for marketplace templates"""

    def __init__(self):
        self.cache_dir = Path(getattr(settings, 'MARKETPLACE_CACHE_DIR', '/tmp/marketplace-cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.hub_local_path = Path(getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub'))

    async def build_app_package(self, app_id: str, version: str) -> dict[str, Any]:
        """
        Build app package (ZIP file)

        Args:
            app_id: Application ID
            version: Application version

        Returns:
            Package info with path, hash, and size
        """
        try:
            # Check cache
            cached = await self.get_cached_package(app_id, version)
            if cached:
                log.info(f"Using cached package for {app_id} v{version}")
                return cached

            # Build package
            log.info(f"Building package for {app_id} v{version}")

            # Get paths
            templates_dir = self.hub_local_path / 'templates'
            base_dir = templates_dir / '_base'
            base_desktop_dir = templates_dir / '_base_desktop'
            app_dir = templates_dir / app_id

            if not app_dir.exists():
                raise FileNotFoundError(f"App directory not found: {app_dir}")

            # Create temporary directory
            tmpdir = Path(tempfile.mkdtemp(prefix=f"huanxing-app-{app_id}-"))

            try:
                # 1. Copy _base directory (if exists)
                if base_dir.exists():
                    dst_base = tmpdir / '_base'
                    shutil.copytree(base_dir, dst_base)
                    log.info(f"Copied _base/ directory")

                # 2. Copy _base_desktop directory (if exists)
                if base_desktop_dir.exists():
                    dst_desktop = tmpdir / '_base_desktop'
                    shutil.copytree(base_desktop_dir, dst_desktop)
                    log.info(f"Copied _base_desktop/ directory")

                # 3. Copy app-specific files (excluding local icons)
                for item in app_dir.iterdir():
                    if item.name.startswith('.'):
                        continue

                    # Skip local icon files (already uploaded to CDN)
                    if item.name in ['icon.png', 'icon.svg', 'icon.jpg', 'icon.jpeg']:
                        log.info(f"Skipping local icon: {item.name}")
                        continue

                    dst = tmpdir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst)
                    else:
                        shutil.copy2(item, dst)

                log.info(f"Copied app-specific files")

                # 4. Create ZIP package
                package_dir = self.cache_dir / 'apps' / app_id
                package_dir.mkdir(parents=True, exist_ok=True)

                zip_path = package_dir / f"{version}.zip"

                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(tmpdir):
                        # Exclude __pycache__, .git, node_modules
                        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules')]

                        for file in files:
                            if file.startswith('.'):
                                continue

                            file_path = Path(root) / file
                            arcname = file_path.relative_to(tmpdir)
                            zf.write(file_path, arcname)

                # 5. Calculate hash and size
                file_hash = await self._calculate_hash(zip_path)
                file_size = zip_path.stat().st_size

                log.info(f"Package built: {zip_path} ({file_size / 1024:.1f} KB)")

                return {
                    'package_path': str(zip_path),
                    'file_hash': file_hash,
                    'file_size': file_size
                }

            finally:
                # Clean up temporary directory
                shutil.rmtree(tmpdir, ignore_errors=True)

        except Exception as e:
            log.error(f"Failed to build app package: {e}")
            raise

    async def get_cached_package(self, app_id: str, version: str) -> dict[str, Any] | None:
        """
        Get cached package if exists

        Args:
            app_id: Application ID
            version: Application version

        Returns:
            Package info or None if not cached
        """
        zip_path = self.cache_dir / 'apps' / app_id / f"{version}.zip"

        if zip_path.exists():
            file_hash = await self._calculate_hash(zip_path)
            file_size = zip_path.stat().st_size

            return {
                'package_path': str(zip_path),
                'file_hash': file_hash,
                'file_size': file_size
            }

        return None

    async def invalidate_cache(self, app_id: str, version: str | None = None):
        """
        Invalidate package cache

        Args:
            app_id: Application ID
            version: Specific version to invalidate, or None for all versions
        """
        if version:
            # Invalidate specific version
            zip_path = self.cache_dir / 'apps' / app_id / f"{version}.zip"
            if zip_path.exists():
                zip_path.unlink()
                log.info(f"Invalidated cache for {app_id} v{version}")
        else:
            # Invalidate all versions
            app_cache_dir = self.cache_dir / 'apps' / app_id
            if app_cache_dir.exists():
                shutil.rmtree(app_cache_dir)
                log.info(f"Invalidated all cache for {app_id}")

    async def cleanup_old_packages(self, keep_versions: int = 3):
        """
        Clean up old package versions

        Args:
            keep_versions: Number of recent versions to keep
        """
        apps_cache_dir = self.cache_dir / 'apps'

        if not apps_cache_dir.exists():
            return

        for app_dir in apps_cache_dir.iterdir():
            if not app_dir.is_dir():
                continue

            # Get all version files sorted by modification time
            version_files = sorted(
                app_dir.glob('*.zip'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Keep only recent versions
            for old_file in version_files[keep_versions:]:
                old_file.unlink()
                log.info(f"Cleaned up old package: {old_file}")

    async def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash string
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()


# Global instance
app_package_service = AppPackageService()
