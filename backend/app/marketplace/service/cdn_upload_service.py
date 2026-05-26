"""
CDN Upload Service for Marketplace

Handles uploading images (icons, screenshots) to CDN and returns CDN URLs.
"""
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

from backend.common.log import log
from backend.core.conf import settings


class CDNUploadService:
    """CDN upload service for marketplace assets"""

    def __init__(self):
        self.cdn_provider = getattr(settings, 'CDN_PROVIDER', 'aliyun')
        self.cdn_bucket = getattr(settings, 'CDN_BUCKET', 'huanxing-marketplace')
        self.cdn_base_url = getattr(settings, 'CDN_BASE_URL', 'https://cdn.huanxing.ai')
        self.cdn_access_key = getattr(settings, 'CDN_ACCESS_KEY', '')
        self.cdn_secret_key = getattr(settings, 'CDN_SECRET_KEY', '')

    async def upload_app_icon(self, app_id: str, icon_file: BinaryIO, filename: str) -> str:
        """
        Upload app icon to CDN

        Args:
            app_id: Application ID
            icon_file: Icon file binary stream
            filename: Original filename

        Returns:
            CDN URL of uploaded icon
        """
        try:
            # Read file content
            content = icon_file.read()

            # Calculate file hash for cache busting
            file_hash = hashlib.sha256(content).hexdigest()[:8]

            # Get file extension
            ext = Path(filename).suffix or '.png'

            # Generate CDN path: marketplace/apps/{app_id}/icon_{hash}.{ext}
            cdn_key = f"marketplace/apps/{app_id}/icon_{file_hash}{ext}"

            # Upload to CDN
            cdn_url = await self._upload_to_cdn(cdn_key, content)

            log.info(f"Uploaded app icon to CDN: {cdn_url}")
            return cdn_url

        except Exception as e:
            log.error(f"Failed to upload app icon to CDN: {e}")
            raise

    async def _upload_to_cdn(self, key: str, content: bytes) -> str:
        """
        Upload file to CDN

        Args:
            key: CDN object key
            content: File content

        Returns:
            CDN URL
        """
        if self.cdn_provider == 'aliyun':
            return await self._upload_to_aliyun_oss(key, content)
        elif self.cdn_provider == 'qiniu':
            return await self._upload_to_qiniu(key, content)
        else:
            raise ValueError(f"Unsupported CDN provider: {self.cdn_provider}")

    async def _upload_to_aliyun_oss(self, key: str, content: bytes) -> str:
        """
        Upload to Aliyun OSS

        Args:
            key: OSS object key
            content: File content

        Returns:
            CDN URL
        """
        try:
            import oss2

            # Create OSS auth
            auth = oss2.Auth(self.cdn_access_key, self.cdn_secret_key)

            # Get OSS endpoint from settings
            endpoint = getattr(settings, 'CDN_ENDPOINT', 'oss-cn-beijing.aliyuncs.com')

            # Create bucket instance
            bucket = oss2.Bucket(auth, endpoint, self.cdn_bucket)

            # Upload file
            result = bucket.put_object(key, content)

            if result.status == 200:
                # Return CDN URL
                cdn_url = f"{self.cdn_base_url}/{key}"
                return cdn_url
            else:
                raise Exception(f"OSS upload failed with status {result.status}")

        except ImportError:
            log.error("oss2 package not installed. Install with: pip install oss2")
            raise
        except Exception as e:
            log.error(f"Failed to upload to Aliyun OSS: {e}")
            raise

    async def _upload_to_qiniu(self, key: str, content: bytes) -> str:
        """
        Upload to Qiniu Cloud

        Args:
            key: Qiniu object key
            content: File content

        Returns:
            CDN URL
        """
        try:
            from qiniu import Auth, put_data

            # Create Qiniu auth
            q = Auth(self.cdn_access_key, self.cdn_secret_key)

            # Generate upload token
            token = q.upload_token(self.cdn_bucket, key, 3600)

            # Upload file
            ret, info = put_data(token, key, content)

            if info.status_code == 200:
                # Return CDN URL
                cdn_url = f"{self.cdn_base_url}/{key}"
                return cdn_url
            else:
                raise Exception(f"Qiniu upload failed with status {info.status_code}")

        except ImportError:
            log.error("qiniu package not installed. Install with: pip install qiniu")
            raise
        except Exception as e:
            log.error(f"Failed to upload to Qiniu: {e}")
            raise

    def validate_image(self, content: bytes, max_size_mb: int = 5) -> bool:
        """
        Validate image file

        Args:
            content: File content
            max_size_mb: Maximum file size in MB

        Returns:
            True if valid, False otherwise
        """
        # Check file size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > max_size_mb:
            log.warning(f"Image file too large: {size_mb:.2f}MB > {max_size_mb}MB")
            return False

        # Check file type (simple magic number check)
        # PNG: 89 50 4E 47
        # JPEG: FF D8 FF
        # SVG: 3C 73 76 67 or 3C 3F 78 6D 6C (<?xml)
        if content[:4] == b'\x89PNG' or \
           content[:3] == b'\xFF\xD8\xFF' or \
           content[:4] == b'<svg' or \
           content[:5] == b'<?xml':
            return True

        log.warning("Invalid image file type")
        return False


# Global instance
cdn_upload_service = CDNUploadService()
