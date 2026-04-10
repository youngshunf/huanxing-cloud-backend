"""技能市场 S3 存储服务

用于上传、下载和管理技能包和应用包
"""
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
from typing import BinaryIO

from opendal import AsyncOperator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.plugin.s3.crud.storage import s3_storage_dao


class MarketplaceStorageService:
    """技能市场存储服务类"""
    
    # 存储路径规范
    SKILLS_PATH = 'marketplace/skills'
    APPS_PATH = 'marketplace/apps'
    
    async def _get_operator(self, db: AsyncSession, storage_id: int | None = None) -> AsyncOperator:
        """
        获取 S3 操作器
        
        :param db: 数据库会话
        :param storage_id: 存储配置ID，为空则使用默认配置
        :return: AsyncOperator
        """
        if storage_id:
            s3_storage = await s3_storage_dao.get(db, storage_id)
        else:
            # 获取默认存储（第一个存储配置）
            storages = await s3_storage_dao.get_all(db)
            s3_storage = storages[0] if storages else None
        
        if not s3_storage:
            raise errors.NotFoundError(msg='S3 存储配置不存在，请先在管理后台配置存储')
        
        return AsyncOperator(
            's3',
            endpoint=s3_storage.endpoint,
            access_key_id=s3_storage.access_key,
            secret_access_key=s3_storage.secret_key,
            bucket=s3_storage.bucket,
            root=s3_storage.prefix or '/',
            region=s3_storage.region or 'any',
        ), s3_storage
    
    @staticmethod
    def _calculate_hash(content: bytes) -> str:
        """计算内容的 SHA256 哈希值"""
        return hashlib.sha256(content).hexdigest()
    
    async def upload_skill_package(
        self,
        db: AsyncSession,
        skill_id: str,
        version: str,
        content: bytes,
        storage_id: int | None = None,
    ) -> tuple[str, str, int]:
        """
        上传技能包
        
        :param db: 数据库会话
        :param skill_id: 技能ID
        :param version: 版本号
        :param content: 文件内容
        :param storage_id: 存储配置ID
        :return: (package_url, file_hash, file_size)
        """
        op, s3_storage = await self._get_operator(db, storage_id)
        
        # 计算哈希和大小
        file_hash = self._calculate_hash(content)
        file_size = len(content)
        
        # 构建存储路径
        path = f'{self.SKILLS_PATH}/{skill_id}/{version}.zip'
        
        # 上传文件
        await op.write(path, content)
        
        # 构建下载 URL
        package_url = self._build_url(s3_storage, path)
        
        return package_url, file_hash, file_size
    
    async def upload_app_package(
        self,
        db: AsyncSession,
        app_id: str,
        version: str,
        content: bytes,
        storage_id: int | None = None,
    ) -> tuple[str, str, int]:
        """
        上传应用包
        
        :param db: 数据库会话
        :param app_id: 应用ID
        :param version: 版本号
        :param content: 文件内容
        :param storage_id: 存储配置ID
        :return: (package_url, file_hash, file_size)
        """
        op, s3_storage = await self._get_operator(db, storage_id)
        
        # 计算哈希和大小
        file_hash = self._calculate_hash(content)
        file_size = len(content)
        
        # 构建存储路径
        path = f'{self.APPS_PATH}/{app_id}/{version}.zip'
        
        # 上传文件
        await op.write(path, content)
        
        # 构建下载 URL
        package_url = self._build_url(s3_storage, path)
        
        return package_url, file_hash, file_size
    
    def _build_url(self, s3_storage, path: str) -> str:
        """
        构建文件访问 URL
        
        :param s3_storage: 存储配置
        :param path: 文件路径
        :return: 完整 URL
        """
        # 如果配置了 CDN 域名，优先使用
        if s3_storage.cdn_domain:
            base_url = s3_storage.cdn_domain.rstrip('/')
            if s3_storage.prefix:
                prefix = s3_storage.prefix.strip('/')
                return f'{base_url}/{prefix}/{path}'
            return f'{base_url}/{path}'
        
        # 使用 S3 原始 URL
        bucket_path = f'/{s3_storage.bucket}'
        if s3_storage.prefix:
            prefix = s3_storage.prefix if s3_storage.prefix.startswith('/') else f'/{s3_storage.prefix}'
            return f'{s3_storage.endpoint}{bucket_path}{prefix}/{path}'
        return f'{s3_storage.endpoint}{bucket_path}/{path}'
    
    async def upload_icon(
        self,
        db: AsyncSession,
        item_type: str,  # 'skill' or 'app'
        item_id: str,
        content: bytes,
        filename: str = 'icon.svg',
        version: str | None = None,
        storage_id: int | None = None,
    ) -> str:
        """
        上传图标
        
        :param db: 数据库会话
        :param item_type: 类型 (skill/app)
        :param item_id: 技能或应用ID
        :param content: 图标内容
        :param filename: 图标文件名 (例如 icon.png, icon.svg)
        :param version: 版本号
        :param storage_id: 存储配置ID
        :return: icon_url
        """
        op, s3_storage = await self._get_operator(db, storage_id)
        
        # 提取扩展名
        import os
        name, ext = os.path.splitext(filename)
        
        base_path = self.SKILLS_PATH if item_type == 'skill' else self.APPS_PATH
        if version:
            path = f'{base_path}/{item_id}/{name}-{version}{ext}'
        else:
            path = f'{base_path}/{item_id}/{filename}'
        
        # 上传文件
        await op.write(path, content)
        
        # 构建 URL
        return self._build_url(s3_storage, path)
    
    async def upload_icon_dedup(
        self,
        db: AsyncSession,
        item_type: str,  # 'skill', 'app' or 'sop'
        item_id: str,
        content: bytes,
        filename: str = 'icon.svg',
        storage_id: int | None = None,
    ) -> str:
        """
        上传图标（hash 去重：内容未变则跳过上传，返回已有 URL）
        """
        op, s3_storage = await self._get_operator(db, storage_id)
        content_hash = self._calculate_hash(content)
        
        import os
        name, ext = os.path.splitext(filename)
        base_path = self.SKILLS_PATH if item_type == 'skill' else self.APPS_PATH
        path = f'{base_path}/{item_id}/{filename}'
        
        # 检查是否已存在同 hash 文件（通过 .sha256 元文件）
        hash_path = f'{path}.sha256'
        try:
            existing_hash = (await op.read(hash_path)).decode()
            if existing_hash.strip() == content_hash:
                return self._build_url(s3_storage, path)  # 跳过上传
        except Exception:
            pass  # 不存在，继续上传
        
        await op.write(path, content)
        await op.write(hash_path, content_hash.encode())  # 保存 hash 元文件
        return self._build_url(s3_storage, path)
    
    async def download_package(
        self,
        db: AsyncSession,
        item_type: str,  # 'skill' or 'app'
        item_id: str,
        version: str,
        storage_id: int | None = None,
    ) -> bytes:
        """
        下载包文件
        
        :param db: 数据库会话
        :param item_type: 类型 (skill/app)
        :param item_id: 技能或应用ID
        :param version: 版本号
        :param storage_id: 存储配置ID
        :return: 文件内容
        """
        op, _ = await self._get_operator(db, storage_id)
        
        # 构建存储路径
        base_path = self.SKILLS_PATH if item_type == 'skill' else self.APPS_PATH
        path = f'{base_path}/{item_id}/{version}.zip'
        
        # 下载文件
        content = await op.read(path)
        return content
    
    async def delete_package(
        self,
        db: AsyncSession,
        item_type: str,  # 'skill' or 'app'
        item_id: str,
        version: str,
        storage_id: int | None = None,
    ) -> None:
        """
        删除包文件
        
        :param db: 数据库会话
        :param item_type: 类型 (skill/app)
        :param item_id: 技能或应用ID
        :param version: 版本号
        :param storage_id: 存储配置ID
        """
        op, _ = await self._get_operator(db, storage_id)
        
        # 构建存储路径
        base_path = self.SKILLS_PATH if item_type == 'skill' else self.APPS_PATH
        path = f'{base_path}/{item_id}/{version}.zip'
        
        # 删除文件
        await op.delete(path)


marketplace_storage_service: MarketplaceStorageService = MarketplaceStorageService()
