"""技能/应用发布 API

提供给 CLI 工具远程发布使用的接口。
使用用户的 LLM API Key 认证，自动获取作者信息。
"""
import hashlib
import tempfile
import zipfile
from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO
from typing import Annotated, Optional

import yaml
import json
from fastapi import APIRouter, Depends, File, Form, Header, UploadFile
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.model.user import User
from backend.app.llm.service.api_key_service import api_key_service
from backend.app.marketplace.model import (
    MarketplaceSkill,
    MarketplaceSkillVersion,
    MarketplaceApp,
    MarketplaceAppVersion,
    MarketplaceSop,
    MarketplaceSopVersion,
)
from backend.app.marketplace.storage.s3_storage import marketplace_storage_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


# ============================================================
# 用户认证信息
# ============================================================

@dataclass
class PublishUser:
    """发布用户信息"""
    user_id: int
    username: str
    nickname: str


# ============================================================
# API Key 认证（使用 LLM API Key）
# ============================================================

async def verify_publish_api_key(
    db: CurrentSession,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> PublishUser:
    """验证发布 API Key 并获取用户信息"""
    if not x_api_key:
        raise errors.AuthorizationError(msg='缺少 API Key')
    
    # 验证 API Key
    api_key_record = await api_key_service.verify_api_key(db, x_api_key)
    
    # 获取用户信息
    stmt = select(User).where(User.id == api_key_record.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise errors.AuthorizationError(msg='用户不存在')
    
    return PublishUser(
        user_id=user.id,
        username=user.username,
        nickname=user.nickname,
    )


# ============================================================
# 响应模型
# ============================================================

class PublishResult(BaseModel):
    """发布结果"""
    id: str
    version: str
    package_url: str
    file_hash: str
    file_size: int


# ============================================================
# 预上传 API
# ============================================================

@router.post('/upload-icon', summary='预上传图标')
async def upload_icon_only(
    db: CurrentSession,
    publish_user: Annotated[PublishUser, Depends(verify_publish_api_key)],
    file: Annotated[UploadFile, File(description='图标文件')],
    item_type: Annotated[str, Form(description='skill/app/sop')] = 'app',
    item_id: Annotated[str, Form(description='技能/应用 ID')] = '',
) -> ResponseSchemaModel:
    """
    预上传图标文件（带 Hash 去重）。
    CLI 会在打包前上传获取 URL。
    """
    content = await file.read()
    icon_url = await marketplace_storage_service.upload_icon_dedup(
        db=db,
        item_type=item_type,
        item_id=item_id,
        content=content,
        filename=file.filename or 'icon.svg',
    )
    return response_base.success(data={'icon_url': icon_url})


# ============================================================
# 技能发布 API
# ============================================================

@router.post('/skill', summary='发布技能包')
async def publish_skill(
    db: CurrentSession,
    publish_user: Annotated[PublishUser, Depends(verify_publish_api_key)],
    file: Annotated[UploadFile, File(description='技能包 ZIP 文件')],
    version: Annotated[str | None, Form(description='版本号，不指定则使用包内版本')] = None,
    changelog: Annotated[str | None, Form(description='更新日志')] = None,
) -> ResponseSchemaModel[PublishResult]:
    """
    发布技能包
    
    上传 ZIP 格式的技能包，包含：
    - config.yaml (必需)
    - SKILL.md (必需)
    - icon.svg (可选)
    """
    # 读取上传的文件
    content = await file.read()
    
    # 解析技能包
    try:
        with zipfile.ZipFile(BytesIO(content), 'r') as zf:
            config = None
            if 'config.toml' in zf.namelist():
                config_content = zf.read('config.toml').decode('utf-8')
                import rtoml
                parsed = rtoml.loads(config_content)
                config = parsed.get('skill', parsed)
            elif 'config.yaml' in zf.namelist():
                config_content = zf.read('config.yaml').decode('utf-8')
                config = yaml.safe_load(config_content)
            elif 'manifest.yaml' in zf.namelist():
                config_content = zf.read('manifest.yaml').decode('utf-8')
                config = yaml.safe_load(config_content)
            else:
                raise errors.RequestError(msg='技能包缺少 config.toml, config.yaml 或 manifest.yaml')
            
            # 验证必需字段
            required_fields = ['id', 'name', 'version', 'description']
            for field in required_fields:
                if not config.get(field):
                    raise errors.RequestError(msg=f'配置缺少必需字段: {field}')
            
            # 读取图标（可选）
            icon_content = None
            icon_filename = 'icon.svg'
            icon_paths = ['icon.png', 'icon.svg', 'icon.jpg', 'assets/icon.png', 'assets/icon.svg']
            for icon_path in icon_paths:
                if icon_path in zf.namelist():
                    icon_content = zf.read(icon_path)
                    import os
                    icon_filename = os.path.basename(icon_path)
                    break
    except zipfile.BadZipFile:
        raise errors.RequestError(msg='无效的 ZIP 文件')
    
    skill_id = config['id']
    final_version = version or config['version']
    
    # 计算哈希
    file_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    
    # 上传到 S3
    package_url, _, _ = await marketplace_storage_service.upload_skill_package(
        db=db,
        skill_id=skill_id,
        version=final_version,
        content=content,
    )
    
    # 上传图标
    icon_url = None
    if icon_content:
        icon_url = await marketplace_storage_service.upload_icon(
            db=db,
            item_type='skill',
            item_id=skill_id,
            content=icon_content,
            filename=icon_filename,
        )
    
    # 更新数据库
    await _save_skill_to_db(
        db=db,
        skill_id=skill_id,
        config=config,
        version=final_version,
        changelog=changelog,
        package_url=package_url,
        file_hash=file_hash,
        file_size=file_size,
        icon_url=icon_url,
        emoji=config.get('emoji'),
        author_id=publish_user.user_id,
        author_name=publish_user.nickname or publish_user.username,
    )
    
    return response_base.success(data=PublishResult(
        id=skill_id,
        version=final_version,
        package_url=package_url,
        file_hash=file_hash,
        file_size=file_size,
    ))


async def _save_skill_to_db(
    db: AsyncSession,
    skill_id: str,
    config: dict,
    version: str,
    changelog: str | None,
    package_url: str,
    file_hash: str,
    file_size: int,
    icon_url: str | None,
    emoji: str | None,
    author_id: int | None = None,
    author_name: str | None = None,
) -> None:
    """保存技能到数据库"""
    # 检查技能是否存在
    stmt = select(MarketplaceSkill).where(MarketplaceSkill.skill_id == skill_id)
    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()
    
    if not skill:
        # 创建新技能
        skill = MarketplaceSkill(
            skill_id=skill_id,
            name=config['name'],
            description=config['description'],
            icon_url=icon_url,
            emoji=emoji,
            author_id=author_id,
            author_name=author_name or config.get('author_name', ''),
            pricing_type=config.get('pricing_type', 'free'),
            price=Decimal('0'),
            tags=','.join(config.get('tags', [])) if config.get('tags') else None,
            category=config.get('category'),
            is_private=False,
            is_official=False,
            download_count=0,
        )
        db.add(skill)
        await db.flush()
    else:
        # 更新技能
        update_data = {
            'name': config['name'],
            'description': config['description'],
            'pricing_type': config.get('pricing_type', 'free'),
            'tags': ','.join(config.get('tags', [])) if config.get('tags') else None,
            'category': config.get('category'),
            'emoji': emoji,
        }
        if icon_url:
            update_data['icon_url'] = icon_url
        # 只有原作者或第一次发布时才更新作者信息
        if author_id and (not skill.author_id or skill.author_id == author_id):
            update_data['author_id'] = author_id
            update_data['author_name'] = author_name
        
        stmt = update(MarketplaceSkill).where(
            MarketplaceSkill.skill_id == skill_id
        ).values(**update_data)
        await db.execute(stmt)
    
    # 清除旧版本的 is_latest 标志
    stmt = update(MarketplaceSkillVersion).where(
        MarketplaceSkillVersion.skill_id == skill_id,
        MarketplaceSkillVersion.is_latest == True,
    ).values(is_latest=False)
    await db.execute(stmt)
    
    # 检查版本是否存在
    stmt = select(MarketplaceSkillVersion).where(
        MarketplaceSkillVersion.skill_id == skill_id,
        MarketplaceSkillVersion.version == version,
    )
    result = await db.execute(stmt)
    existing_version = result.scalar_one_or_none()
    
    if existing_version:
        # 更新版本
        stmt = update(MarketplaceSkillVersion).where(
            MarketplaceSkillVersion.skill_id == skill_id,
            MarketplaceSkillVersion.version == version,
        ).values(
            changelog=changelog,
            package_url=package_url,
            file_hash=file_hash,
            file_size=file_size,
            is_latest=True,
        )
        await db.execute(stmt)
    else:
        # 创建版本
        skill_version = MarketplaceSkillVersion(
            skill_id=skill_id,
            version=version,
            changelog=changelog,
            package_url=package_url,
            file_hash=file_hash,
            file_size=file_size,
            is_latest=True,
        )
        db.add(skill_version)
    
    await db.commit()


# ============================================================
# 应用发布 API
# ============================================================

@router.post('/app', summary='发布应用包')
async def publish_app(
    db: CurrentSession,
    publish_user: Annotated[PublishUser, Depends(verify_publish_api_key)],
    file: Annotated[UploadFile, File(description='应用包 ZIP 文件')],
    version: Annotated[str | None, Form(description='版本号，不指定则使用包内版本')] = None,
    changelog: Annotated[str | None, Form(description='更新日志')] = None,
) -> ResponseSchemaModel[PublishResult]:
    """
    发布应用包
    
    上传 ZIP 格式的应用包，包含：
    - manifest.json (必需)
    - assets/icon.svg (可选)
    """
    # 读取上传的文件
    content = await file.read()
    
    # 解析应用包
    try:
        with zipfile.ZipFile(BytesIO(content), 'r') as zf:
            manifest = None
            if 'config.toml' in zf.namelist():
                manifest_content = zf.read('config.toml').decode('utf-8')
                import rtoml
                parsed = rtoml.loads(manifest_content)
                agent_info = parsed.get('agent', {})
                manifest = {
                    'id': agent_info.get('name') or parsed.get('id'),
                    'name': agent_info.get('display_name') or agent_info.get('name') or parsed.get('name'),
                    'emoji': agent_info.get('emoji') or parsed.get('emoji'),
                    'version': agent_info.get('version') or parsed.get('version', '1.0.0'),
                    'description': agent_info.get('description') or parsed.get('description', 'Agent App'),
                    'skill_dependencies': parsed.get('plugins', {}).get('skills', []) if isinstance(parsed.get('plugins'), dict) else [],
                    'pricing_type': parsed.get('marketplace', {}).get('pricing_type', 'free'),
                    'category': parsed.get('marketplace', {}).get('category'),
                    'tags': parsed.get('marketplace', {}).get('tags', []),
                }
            elif 'manifest.json' in zf.namelist():
                manifest_content = zf.read('manifest.json').decode('utf-8')
                manifest = json.loads(manifest_content)
            elif 'template.yaml' in zf.namelist():
                template_content = zf.read('template.yaml').decode('utf-8')
                import yaml
                parsed = yaml.safe_load(template_content) or {}
                manifest = {
                    'id': parsed.get('id', parsed.get('name', 'unknown-app')),
                    'name': parsed.get('display_name') or parsed.get('name', 'unknown-name'),
                    'emoji': parsed.get('emoji'),
                    'version': parsed.get('version', '1.0.0'),
                    'description': parsed.get('description', 'Agent App'),
                    'skill_dependencies': parsed.get('skills', []),
                    'sop_dependencies': parsed.get('sops', []),
                    'pricing_type': parsed.get('pricing_type', 'free'),
                    'category': parsed.get('category'),
                    'tags': parsed.get('tags', []),
                }
            else:
                raise errors.RequestError(msg='应用包缺少 config.toml, manifest.json 或 template.yaml')
            
            # 验证必需字段
            required_fields = ['id', 'name', 'version', 'description']
            for field in required_fields:
                if not manifest.get(field):
                    raise errors.RequestError(msg=f'配置缺少必需字段: {field}')
            
            # 读取图标（可选，支持多种路径）
            icon_content = None
            icon_filename = 'icon.svg'
            icon_paths = ['icon.png', 'icon.svg', 'icon.jpg', 'assets/icon.png', 'assets/icon.svg']
            for icon_path in icon_paths:
                if icon_path in zf.namelist():
                    icon_content = zf.read(icon_path)
                    import os
                    icon_filename = os.path.basename(icon_path)
                    break
    except zipfile.BadZipFile:
        raise errors.RequestError(msg='无效的 ZIP 文件')
    except json.JSONDecodeError:
        raise errors.RequestError(msg='manifest.json 格式错误')
    
    app_id = manifest['id']
    final_version = version or manifest['version']
    
    # 计算哈希
    file_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    
    # 上传到 S3
    package_url, _, _ = await marketplace_storage_service.upload_app_package(
        db=db,
        app_id=app_id,
        version=final_version,
        content=content,
    )
    
    # 上传图标
    icon_url = None
    if icon_content:
        icon_url = await marketplace_storage_service.upload_icon(
            db=db,
            item_type='app',
            item_id=app_id,
            content=icon_content,
            filename=icon_filename,
        )
    
    # 更新数据库
    await _save_app_to_db(
        db=db,
        app_id=app_id,
        manifest=manifest,
        version=final_version,
        changelog=changelog,
        package_url=package_url,
        file_hash=file_hash,
        file_size=file_size,
        icon_url=icon_url,
        emoji=manifest.get('emoji'),
        author_id=publish_user.user_id,
        author_name=publish_user.nickname or publish_user.username,
    )
    
    return response_base.success(data=PublishResult(
        id=app_id,
        version=final_version,
        package_url=package_url,
        file_hash=file_hash,
        file_size=file_size,
    ))


# ============================================================
# SOP 发布 API
# ============================================================

@router.post('/sop', summary='发布SOP工作流包')
async def publish_sop(
    db: CurrentSession,
    publish_user: Annotated[PublishUser, Depends(verify_publish_api_key)],
    file: Annotated[UploadFile, File(description='SOP包 ZIP 文件')],
    version: Annotated[str | None, Form(description='版本号')] = None,
    changelog: Annotated[str | None, Form(description='更新日志')] = None,
) -> ResponseSchemaModel[PublishResult]:
    """
    发布SOP工作流包
    
    上传 ZIP 格式的SOP包，包含：
    - SOP.toml (必需)
    - SOP.md (必需)
    - icon.svg (可选)
    """
    content = await file.read()
    
    try:
        with zipfile.ZipFile(BytesIO(content), 'r') as zf:
            # 解析 SOP.toml
            if 'SOP.toml' not in zf.namelist():
                raise errors.RequestError(msg='SOP包缺少 SOP.toml')
            
            import rtoml
            toml_content = zf.read('SOP.toml').decode('utf-8')
            parsed = rtoml.loads(toml_content)
            sop_meta = parsed.get('sop', {})
            
            sop_id = sop_meta.get('name')
            if not sop_id:
                raise errors.RequestError(msg='SOP.toml 缺少 name 字段')
            
            description = sop_meta.get('description', '')
            sop_version = version or sop_meta.get('version', '1.0.0')
            execution_mode = sop_meta.get('execution_mode', 'supervised')
            emoji = sop_meta.get('emoji')
            category = sop_meta.get('category')
            tags = sop_meta.get('tags', [])
            
            # 从 SOP.md 提取 skill 依赖
            skill_deps = []
            if 'SOP.md' in zf.namelist():
                md_content = zf.read('SOP.md').decode('utf-8')
                import re
                # 匹配 `- tools: xxx, yyy, zzz` 行
                for match in re.finditer(r'-\s*tools:\s*(.+)', md_content):
                    tools_str = match.group(1).strip()
                    for tool in tools_str.split(','):
                        tool = tool.strip()
                        if tool and tool not in skill_deps:
                            skill_deps.append(tool)
            
            # 读取图标
            icon_content = None
            icon_filename = 'icon.svg'
            icon_paths = ['icon.png', 'icon.svg', 'icon.jpg', 'assets/icon.png', 'assets/icon.svg']
            for icon_path in icon_paths:
                if icon_path in zf.namelist():
                    icon_content = zf.read(icon_path)
                    import os
                    icon_filename = os.path.basename(icon_path)
                    break
                
    except zipfile.BadZipFile:
        raise errors.RequestError(msg='无效的 ZIP 文件')
    
    # 计算哈希
    file_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    
    # 上传到 S3
    package_url, _, _ = await marketplace_storage_service.upload_app_package(
        db=db,
        app_id=sop_id,
        version=sop_version,
        content=content,
    )
    
    # 上传图标
    icon_url = None
    if icon_content:
        icon_url = await marketplace_storage_service.upload_icon(
            db=db,
            item_type='sop',
            item_id=sop_id,
            content=icon_content,
            filename=icon_filename,
        )
    
    # 保存到数据库
    await _save_sop_to_db(
        db=db,
        sop_id=sop_id,
        name=sop_meta.get('display_name') or sop_meta.get('name', sop_id),
        description=description,
        version=sop_version,
        changelog=changelog,
        package_url=package_url,
        file_hash=file_hash,
        file_size=file_size,
        icon_url=icon_url,
        emoji=emoji,
        execution_mode=str(execution_mode) if execution_mode else 'supervised',
        skill_dependencies=','.join(skill_deps) if skill_deps else None,
        category=category,
        tags=','.join(tags) if isinstance(tags, list) else tags,
        author_id=publish_user.user_id,
        author_name=publish_user.nickname or publish_user.username,
    )
    
    return response_base.success(data=PublishResult(
        id=sop_id,
        version=sop_version,
        package_url=package_url,
        file_hash=file_hash,
        file_size=file_size,
    ))


async def _save_app_to_db(
    db: AsyncSession,
    app_id: str,
    manifest: dict,
    version: str,
    changelog: str | None,
    package_url: str,
    file_hash: str,
    file_size: int,
    icon_url: str | None,
    emoji: str | None,
    author_id: int | None = None,
    author_name: str | None = None,
) -> None:
    """保存应用到数据库"""
    # 从 capabilities.skills 或 skill_dependencies 读取技能依赖
    capabilities = manifest.get('capabilities', {})
    skill_dependencies = capabilities.get('skills', []) or manifest.get('skill_dependencies', [])
    skill_deps_str = ','.join(skill_dependencies) if skill_dependencies else None

    # 读取 SOP 依赖
    sop_dependencies = manifest.get('sops', []) or manifest.get('sop_dependencies', [])
    sop_deps_str = ','.join(sop_dependencies) if sop_dependencies else None

    # 读取 marketplace 元数据（兼容嵌套和顶层两种格式）
    marketplace_meta = manifest.get('marketplace', {})
    app_category = marketplace_meta.get('category') or manifest.get('category')
    app_tags_list = marketplace_meta.get('tags') or manifest.get('tags', [])
    app_tags = ','.join(app_tags_list) if app_tags_list else None
    
    # 检查应用是否存在
    stmt = select(MarketplaceApp).where(MarketplaceApp.app_id == app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    
    if not app:
        # 创建新应用
        app = MarketplaceApp(
            app_id=app_id,
            name=manifest['name'],
            description=manifest['description'],
            icon_url=icon_url,
            emoji=emoji,
            author_id=author_id,
            author_name=author_name or manifest.get('author_name', ''),
            pricing_type=manifest.get('pricing_type') or manifest.get('pricing', {}).get('type', 'free'),
            price=Decimal('0'),
            skill_dependencies=skill_deps_str,
            sop_dependencies=sop_deps_str,
            category=app_category,
            tags=app_tags,
            is_private=False,
            is_official=False,
            download_count=0,
        )
        db.add(app)
        await db.flush()
    else:
        # 更新应用
        update_data = {
            'name': manifest['name'],
            'description': manifest['description'],
            'pricing_type': manifest.get('pricing_type') or manifest.get('pricing', {}).get('type', 'free'),
            'skill_dependencies': skill_deps_str,
            'sop_dependencies': sop_deps_str,
            'category': app_category,
            'tags': app_tags,
            'emoji': emoji,
        }
        if icon_url:
            update_data['icon_url'] = icon_url
        # 只有原作者或第一次发布时才更新作者信息
        if author_id and (not app.author_id or app.author_id == author_id):
            update_data['author_id'] = author_id
            update_data['author_name'] = author_name
        
        stmt = update(MarketplaceApp).where(
            MarketplaceApp.app_id == app_id
        ).values(**update_data)
        await db.execute(stmt)
    
    # 清除旧版本的 is_latest 标志
    stmt = update(MarketplaceAppVersion).where(
        MarketplaceAppVersion.app_id == app_id,
        MarketplaceAppVersion.is_latest == True,
    ).values(is_latest=False)
    await db.execute(stmt)
    
    # 版本化的技能依赖
    skill_deps_versioned = {}
    for dep in skill_dependencies:
        if '@' in dep:
            sid, ver = dep.split('@', 1)
            skill_deps_versioned[sid] = ver
        else:
            skill_deps_versioned[dep] = '*'
    
    # 检查版本是否存在
    stmt = select(MarketplaceAppVersion).where(
        MarketplaceAppVersion.app_id == app_id,
        MarketplaceAppVersion.version == version,
    )
    result = await db.execute(stmt)
    existing_version = result.scalar_one_or_none()
    
    if existing_version:
        # 更新版本
        stmt = update(MarketplaceAppVersion).where(
            MarketplaceAppVersion.app_id == app_id,
            MarketplaceAppVersion.version == version,
        ).values(
            changelog=changelog,
            skill_dependencies_versioned=skill_deps_versioned if skill_deps_versioned else None,
            package_url=package_url,
            file_hash=file_hash,
            file_size=file_size,
            is_latest=True,
        )
        await db.execute(stmt)
    else:
        # 创建版本
        app_version = MarketplaceAppVersion(
            app_id=app_id,
            version=version,
            changelog=changelog,
            skill_dependencies_versioned=skill_deps_versioned if skill_deps_versioned else None,
            package_url=package_url,
            file_hash=file_hash,
            file_size=file_size,
            is_latest=True,
        )
        db.add(app_version)
    
    await db.commit()


async def _save_sop_to_db(
    db: AsyncSession,
    sop_id: str,
    name: str,
    description: str,
    version: str,
    changelog: str | None,
    package_url: str,
    file_hash: str,
    file_size: int,
    icon_url: str | None,
    emoji: str | None,
    execution_mode: str = 'supervised',
    skill_dependencies: str | None = None,
    category: str | None = None,
    tags: str | None = None,
    author_id: int | None = None,
    author_name: str | None = None,
) -> None:
    """保存SOP到数据库"""
    # 检查SOP是否存在
    stmt = select(MarketplaceSop).where(MarketplaceSop.sop_id == sop_id)
    result = await db.execute(stmt)
    sop = result.scalar_one_or_none()
    
    if not sop:
        sop = MarketplaceSop(
            sop_id=sop_id,
            name=name,
            description=description,
            icon_url=icon_url,
            emoji=emoji,
            author_id=author_id,
            author_name=author_name or '',
            category=category,
            tags=tags,
            execution_mode=execution_mode,
            skill_dependencies=skill_dependencies,
            pricing_type='free',
            price=Decimal('0'),
            is_private=False,
            is_official=False,
            download_count=0,
        )
        db.add(sop)
        await db.flush()
    else:
        update_data = {
            'name': name,
            'description': description,
            'execution_mode': execution_mode,
            'skill_dependencies': skill_dependencies,
            'category': category,
            'tags': tags,
            'emoji': emoji,
        }
        if icon_url:
            update_data['icon_url'] = icon_url
        if author_id and (not sop.author_id or sop.author_id == author_id):
            update_data['author_id'] = author_id
            update_data['author_name'] = author_name
        
        stmt = update(MarketplaceSop).where(
            MarketplaceSop.sop_id == sop_id
        ).values(**update_data)
        await db.execute(stmt)
    
    # 清除旧版本的 is_latest 标志
    stmt = update(MarketplaceSopVersion).where(
        MarketplaceSopVersion.sop_id == sop_id,
        MarketplaceSopVersion.is_latest == True,
    ).values(is_latest=False)
    await db.execute(stmt)
    
    # 检查版本是否存在
    stmt = select(MarketplaceSopVersion).where(
        MarketplaceSopVersion.sop_id == sop_id,
        MarketplaceSopVersion.version == version,
    )
    result = await db.execute(stmt)
    existing_version = result.scalar_one_or_none()
    
    if existing_version:
        stmt = update(MarketplaceSopVersion).where(
            MarketplaceSopVersion.sop_id == sop_id,
            MarketplaceSopVersion.version == version,
        ).values(
            changelog=changelog,
            package_url=package_url,
            file_hash=file_hash,
            file_size=file_size,
            is_latest=True,
        )
        await db.execute(stmt)
    else:
        sop_version = MarketplaceSopVersion(
            sop_id=sop_id,
            version=version,
            changelog=changelog,
            package_url=package_url,
            file_hash=file_hash,
            file_size=file_size,
            is_latest=True,
        )
        db.add(sop_version)
    
    await db.commit()
