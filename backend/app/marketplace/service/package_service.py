"""
Package Service for Marketplace Skills

Handles skill packaging, caching, and download.
"""
import hashlib
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao
from backend.app.marketplace.crud.crud_marketplace_skill_version import marketplace_skill_version_dao
from backend.common.log import log
from backend.core.conf import settings


class PackageService:
    """Package service for marketplace skills"""

    def __init__(self):
        self.cache_dir = Path(getattr(settings, 'SKILL_PACKAGE_CACHE_DIR', '/tmp/skill-packages'))
        self.hub_repo_path = Path(getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub'))

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_skill_package(
        self,
        db: AsyncSession,
        skill_id: str,
        version: str | None = None
    ) -> tuple[Path, str]:
        """
        Get skill package (zip file)

        Args:
            db: Database session
            skill_id: Skill ID (e.g., "automation/auto-commit")
            version: Version (use latest if None)

        Returns:
            Tuple of (package_path, package_hash)
        """
        # Get skill from database
        skill = await marketplace_skill_dao.get_by_id(db, skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        # Get version
        if version is None:
            version = skill.latest_version or '1.0.0'

        # Check cache
        cache_key = f"{skill_id.replace('/', '_')}_{version}"
        cached_package = self.cache_dir / f"{cache_key}.zip"

        if cached_package.exists():
            # Verify hash
            cached_hash = await self._calculate_file_hash(cached_package)

            # Check if package is up-to-date
            skill_version = await marketplace_skill_version_dao.get_by_skill_and_version(
                db, skill_id, version
            )

            if skill_version and skill_version.file_hash == cached_hash:
                log.info(f"Using cached package for {skill_id}@{version}")
                return cached_package, cached_hash

        # Package not cached or outdated, create new package
        log.info(f"Creating package for {skill_id}@{version}")
        package_path, package_hash = await self._create_package(skill, version)

        # Note: Version record update skipped for now
        # TODO: Implement partial update for version metadata

        return package_path, package_hash

    async def _create_package(self, skill, version: str) -> tuple[Path, str]:
        """
        Create a zip package for a skill

        Args:
            skill: Skill model instance
            version: Version string

        Returns:
            Tuple of (package_path, package_hash)
        """
        # Get skill directory
        skill_dir = self.hub_repo_path / skill.repo_path
        if not skill_dir.exists():
            raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

        # Create package filename
        cache_key = f"{skill.skill_id.replace('/', '_')}_{version}"
        package_path = self.cache_dir / f"{cache_key}.zip"

        # Create zip file
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(skill_dir):
                # Skip hidden directories and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

                for file in files:
                    # Skip hidden files and .pyc files
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(skill_dir)
                    zipf.write(file_path, arcname)

        # Calculate hash
        package_hash = await self._calculate_file_hash(package_path)

        log.info(f"Created package: {package_path} (hash: {package_hash})")
        return package_path, package_hash

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file

        Args:
            file_path: Path to file

        Returns:
            Hex digest of hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def clear_cache(self, skill_id: str | None = None):
        """
        Clear package cache

        Args:
            skill_id: Clear cache for specific skill (or all if None)
        """
        if skill_id:
            # Clear specific skill
            pattern = f"{skill_id.replace('/', '_')}_*.zip"
            for package_file in self.cache_dir.glob(pattern):
                package_file.unlink()
                log.info(f"Cleared cache: {package_file}")
        else:
            # Clear all cache
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            log.info("Cleared all package cache")

    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dict with cache stats
        """
        total_size = 0
        file_count = 0

        for package_file in self.cache_dir.glob('*.zip'):
            total_size += package_file.stat().st_size
            file_count += 1

        return {
            'file_count': file_count,
            'total_size': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'cache_dir': str(self.cache_dir)
        }

    def get_package_stream(self, package_path: Path) -> BinaryIO:
        """
        Get package file stream for download

        Args:
            package_path: Path to package file

        Returns:
            Binary file stream
        """
        return open(package_path, 'rb')


# Singleton instance
package_service = PackageService()
