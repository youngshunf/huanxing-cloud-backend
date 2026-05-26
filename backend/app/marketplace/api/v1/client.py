"""桌面端公开 API

提供给桌面应用使用的公开接口，不需要登录认证。
仅支持读取操作（列表、详情、搜索）和下载。
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel
import os
import yaml

from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao
from backend.app.marketplace.crud.crud_marketplace_skill_version import marketplace_skill_version_dao
from backend.app.marketplace.crud.crud_marketplace_template import marketplace_template_dao
from backend.app.marketplace.crud.crud_marketplace_template_version import marketplace_template_version_dao
from backend.app.marketplace.crud.crud_marketplace_sop import marketplace_sop_dao
from backend.app.marketplace.crud.crud_marketplace_sop_version import marketplace_sop_version_dao
from backend.app.marketplace.crud.crud_marketplace_category import marketplace_category_dao
from backend.app.marketplace.schema.marketplace_skill import GetMarketplaceSkillDetail
from backend.app.marketplace.schema.marketplace_skill_version import GetMarketplaceSkillVersionDetail
from backend.app.marketplace.schema.marketplace_template import GetMarketplaceTemplateDetail
from backend.app.marketplace.schema.marketplace_template_version import GetMarketplaceTemplateVersionDetail
from backend.app.marketplace.schema.marketplace_sop import GetMarketplaceSopDetail
from backend.app.marketplace.schema.marketplace_sop_version import GetMarketplaceSopVersionDetail
from backend.app.marketplace.schema.marketplace_category import GetMarketplaceCategoryDetail
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


# ============================================================
# 公开的配置 API
# ============================================================

@router.get('/common-skills', summary='公开接口：获取全局公共技能配置')
async def get_common_skills() -> ResponseSchemaModel[dict]:
    """获取云端的 common-skills 配置，用于向桌面端下发内置技能更新列表"""
    # 临时从本地 huanxing-hub 中读取，未来可改为从数据库或配置中心获取
    # 这里使用环境变量或默认路径作为过渡
    hub_path = os.environ.get('HUANXING_HUB_DIR', '../huanxing-hub')
    
    # 尝试多种可能的路径
    for path_candidate in [hub_path, '/Users/mac/openclaw-workspace/huanxing/huanxing-project/huanxing-hub']:
        yaml_file = os.path.join(path_candidate, 'common-skills.yaml')
        if os.path.exists(yaml_file):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return response_base.success(data=data)
    
    # 缺省空结构
    return response_base.success(data={"version": "1.0", "skills": []})


# ============================================================
# 公开的技能列表 API
# ============================================================

@router.get('/skills', summary='公开接口：获取技能列表', dependencies=[DependsPagination])
async def list_skills(
    db: CurrentSession,
    category: Optional[str] = Query(None, description='分类筛选'),
    tags: Optional[str] = Query(None, description='标签筛选'),
    pricing_type: Optional[str] = Query(None, description='定价类型: free/paid'),
    is_official: Optional[bool] = Query(None, description='是否官方'),
) -> ResponseSchemaModel[PageData[GetMarketplaceSkillDetail]]:
    """公开的技能列表接口，无需登录"""
    skill_select = await marketplace_skill_dao.get_select_public(
        category=category,
        tags=tags,
        pricing_type=pricing_type,
        is_official=is_official,
    )
    page_data = await paging_data(db, skill_select)
    
    # 填充 latest_version 字段
    for item in page_data['items']:
        latest = await marketplace_skill_version_dao.get_latest_by_skill(db, item['skill_id'])
        item['latest_version'] = latest.version if latest else None
    
    return response_base.success(data=page_data)


@router.get('/skills/{skill_id}', summary='公开接口：获取技能详情')
async def get_skill(
    db: CurrentSession,
    skill_id: Annotated[str, Path(description='技能ID')],
) -> ResponseSchemaModel[GetMarketplaceSkillDetail]:
    """公开的技能详情接口，无需登录"""
    skill = await marketplace_skill_dao.get_by_id(db, skill_id)
    if not skill:
        raise errors.NotFoundError(msg='技能不存在')
    
    # 转换为 schema 并填充 latest_version 字段
    skill_data = GetMarketplaceSkillDetail.model_validate(skill)
    latest = await marketplace_skill_version_dao.get_latest_by_skill(db, skill_id)
    skill_data.latest_version = latest.version if latest else None
    
    return response_base.success(data=skill_data)


@router.get('/skills/{skill_id}/versions', summary='公开接口：获取技能版本列表')
async def get_skill_versions(
    db: CurrentSession,
    skill_id: Annotated[str, Path(description='技能ID')],
) -> ResponseSchemaModel[list[GetMarketplaceSkillVersionDetail]]:
    """公开的技能版本列表接口，无需登录"""
    versions = await marketplace_skill_version_dao.get_by_skill(db, skill_id)
    return response_base.success(data=versions)


# ============================================================
# 公开的应用列表 API
# ============================================================

@router.get('/apps', summary='公开接口：获取应用列表', dependencies=[DependsPagination])
async def list_apps(
    db: CurrentSession,
    category: Optional[str] = Query(None, description='分类筛选'),
    pricing_type: Optional[str] = Query(None, description='定价类型: free/paid/subscription'),
    is_official: Optional[bool] = Query(None, description='是否官方'),
) -> ResponseSchemaModel[PageData[GetMarketplaceTemplateDetail]]:
    """公开的应用列表接口，无需登录"""
    app_select = await marketplace_template_dao.get_select_public(
        category=category,
        pricing_type=pricing_type,
        is_official=is_official,
    )
    page_data = await paging_data(db, app_select)
    
    # 填充 latest_version 字段
    for item in page_data['items']:
        latest = await marketplace_template_version_dao.get_latest_by_app(db, item['template_id'])
        item['latest_version'] = latest.version if latest else None
    
    return response_base.success(data=page_data)


@router.get('/apps/{template_id}', summary='公开接口：获取应用详情')
async def get_app(
    db: CurrentSession,
    template_id: Annotated[str, Path(description='应用ID')],
) -> ResponseSchemaModel[GetMarketplaceTemplateDetail]:
    """公开的应用详情接口，无需登录"""
    app = await marketplace_template_dao.get_by_id(db, template_id)
    if not app:
        raise errors.NotFoundError(msg='应用不存在')
    
    # 转换为 schema 并填充 latest_version 字段
    app_data = GetMarketplaceTemplateDetail.model_validate(app)
    latest = await marketplace_template_version_dao.get_latest_by_app(db, template_id)
    app_data.latest_version = latest.version if latest else None
    
    return response_base.success(data=app_data)


@router.get('/apps/{template_id}/versions', summary='公开接口：获取应用版本列表', name='marketplace_get_app_versions')
async def get_app_versions(
    db: CurrentSession,
    template_id: Annotated[str, Path(description='应用ID')],
) -> ResponseSchemaModel[list[GetMarketplaceTemplateVersionDetail]]:
    """公开的应用版本列表接口，无需登录"""
    versions = await marketplace_template_version_dao.get_by_app(db, template_id)
    return response_base.success(data=versions)


@router.get('/apps/{template_id}/skills', summary='公开接口：获取应用包含的技能列表')
async def get_app_skills(
    db: CurrentSession,
    template_id: Annotated[str, Path(description='应用ID')],
) -> ResponseSchemaModel[list[GetMarketplaceSkillDetail]]:
    """根据应用ID获取其包含的技能列表，一次性返回所有技能详情"""
    app = await marketplace_template_dao.get_by_id(db, template_id)
    if not app:
        raise errors.NotFoundError(msg='应用不存在')
    
    # 解析技能依赖列表
    if not app.skill_dependencies:
        return response_base.success(data=[])
    
    skill_ids = [s.strip() for s in app.skill_dependencies.split(',') if s.strip()]
    if not skill_ids:
        return response_base.success(data=[])
    
    # 批量获取技能详情
    skills = []
    for skill_id in skill_ids:
        skill = await marketplace_skill_dao.get_by_id(db, skill_id)
        if skill:
            skill_data = GetMarketplaceSkillDetail.model_validate(skill)
            latest = await marketplace_skill_version_dao.get_latest_by_skill(db, skill_id)
            skill_data.latest_version = latest.version if latest else None
            skills.append(skill_data)
    
    return response_base.success(data=skills)


# ============================================================
# 公开的搜索 API
# ============================================================

class SearchResult(BaseModel):
    """搜索结果"""
    skills: list[GetMarketplaceSkillDetail]
    apps: list[GetMarketplaceTemplateDetail]


@router.get('/search', summary='公开接口：搜索技能和应用')
async def client_search(
    db: CurrentSession,
    q: str = Query(..., min_length=1, description='搜索关键词'),
    type: Optional[str] = Query('all', description='类型: skill/app/all'),
    category: Optional[str] = Query(None, description='分类筛选'),
    limit: int = Query(20, ge=1, le=50, description='每类最大结果数'),
) -> ResponseSchemaModel[SearchResult]:
    """公开的搜索接口，无需登录"""
    skills = []
    apps = []
    
    if type in ('all', 'skill'):
        skill_results = await marketplace_skill_dao.search(
            db=db,
            keyword=q,
            category=category,
            limit=limit,
        )
        # 转换为 schema 并填充 latest_version 字段
        for skill in skill_results:
            skill_data = GetMarketplaceSkillDetail.model_validate(skill)
            latest = await marketplace_skill_version_dao.get_latest_by_skill(db, skill.skill_id)
            skill_data.latest_version = latest.version if latest else None
            skills.append(skill_data)
    
    if type in ('all', 'app'):
        app_results = await marketplace_template_dao.search(
            db=db,
            keyword=q,
            category=category,
            limit=limit,
        )
        # 转换为 schema 并填充 latest_version 字段
        for app in app_results:
            app_data = GetMarketplaceTemplateDetail.model_validate(app)
            latest = await marketplace_template_version_dao.get_latest_by_app(db, app.template_id)
            app_data.latest_version = latest.version if latest else None
            apps.append(app_data)
    
    return response_base.success(data=SearchResult(skills=skills, apps=apps))


# ============================================================
# 下载 API
# ============================================================

class DownloadInfo(BaseModel):
    """下载信息"""
    id: str
    version: str
    package_url: str
    file_hash: str | None
    file_size: int | None


class AppDownloadInfo(DownloadInfo):
    """应用下载信息，包含技能依赖"""
    skill_dependencies: list[dict] | None = None


@router.get('/download/skill/{skill_id}/latest', summary='公开接口：获取技能最新版本下载信息')
async def download_skill_latest(
    db: CurrentSession,
    skill_id: Annotated[str, Path(description='技能ID')],
) -> ResponseSchemaModel[DownloadInfo]:
    """获取技能最新版本的下载信息"""
    version = await marketplace_skill_version_dao.get_latest_by_skill(db, skill_id)
    if not version:
        raise errors.NotFoundError(msg='技能或版本不存在')
    
    # 增加下载计数
    await marketplace_skill_dao.increment_download_count(db, skill_id)
    await db.commit()
    
    return response_base.success(data=DownloadInfo(
        id=skill_id,
        version=version.version,
        package_url=version.package_url,
        file_hash=version.file_hash,
        file_size=version.file_size,
    ))


@router.get('/download/skill/{skill_id}/{version}', summary='公开接口：获取技能指定版本下载信息')
async def download_skill_version(
    db: CurrentSession,
    skill_id: Annotated[str, Path(description='技能ID')],
    version: Annotated[str, Path(description='版本号')],
) -> ResponseSchemaModel[DownloadInfo]:
    """获取技能指定版本的下载信息"""
    ver = await marketplace_skill_version_dao.get_by_skill_and_version(db, skill_id, version)
    if not ver:
        raise errors.NotFoundError(msg='技能或版本不存在')
    
    # 增加下载计数
    await marketplace_skill_dao.increment_download_count(db, skill_id)
    await db.commit()
    
    return response_base.success(data=DownloadInfo(
        id=skill_id,
        version=ver.version,
        package_url=ver.package_url,
        file_hash=ver.file_hash,
        file_size=ver.file_size,
    ))


@router.get('/download/app/{template_id}/latest', summary='公开接口：获取应用最新版本下载信息')
async def download_app_latest(
    db: CurrentSession,
    template_id: Annotated[str, Path(description='应用ID')],
) -> ResponseSchemaModel[AppDownloadInfo]:
    """获取应用最新版本的下载信息"""
    # 获取应用信息（用于回退获取 skill_dependencies）
    app = await marketplace_template_dao.get_by_id(db, template_id)
    if not app:
        raise errors.NotFoundError(msg='应用不存在')
    
    version = await marketplace_template_version_dao.get_latest_by_app(db, template_id)
    if not version:
        raise errors.NotFoundError(msg='应用版本不存在')
    
    # 增加下载计数
    await marketplace_template_dao.increment_download_count(db, template_id)
    await db.commit()
    
    # 解析技能依赖：优先使用版本级别的 skill_dependencies_versioned，回退到应用级别的 skill_dependencies
    skill_dependencies = []
    skill_ids = []
    
    if version.skill_dependencies_versioned:
        skill_ids = list(version.skill_dependencies_versioned.keys())
    elif app.skill_dependencies:
        skill_ids = [s.strip() for s in app.skill_dependencies.split(',') if s.strip()]
    
    for skill_id in skill_ids:
        skill_ver = await marketplace_skill_version_dao.get_latest_by_skill(db, skill_id)
        if skill_ver and skill_ver.package_url:
            skill_dependencies.append({
                'id': skill_id,
                'version': skill_ver.version,
                'download_url': skill_ver.package_url,
                'file_hash': skill_ver.file_hash,
            })
    
    return response_base.success(data=AppDownloadInfo(
        id=template_id,
        version=version.version,
        package_url=version.package_url,
        file_hash=version.file_hash,
        file_size=version.file_size,
        skill_dependencies=skill_dependencies if skill_dependencies else None,
    ))


@router.get('/download/app/{template_id}/{version}', summary='公开接口：获取应用指定版本下载信息')
async def download_app_version(
    db: CurrentSession,
    template_id: Annotated[str, Path(description='应用ID')],
    version: Annotated[str, Path(description='版本号')],
) -> ResponseSchemaModel[AppDownloadInfo]:
    """获取应用指定版本的下载信息"""
    # 获取应用信息（用于回退获取 skill_dependencies）
    app = await marketplace_template_dao.get_by_id(db, template_id)
    if not app:
        raise errors.NotFoundError(msg='应用不存在')
    
    ver = await marketplace_template_version_dao.get_by_app_and_version(db, template_id, version)
    if not ver:
        raise errors.NotFoundError(msg='应用版本不存在')
    
    # 增加下载计数
    await marketplace_template_dao.increment_download_count(db, template_id)
    await db.commit()
    
    # 解析技能依赖：优先使用版本级别的 skill_dependencies_versioned，回退到应用级别的 skill_dependencies
    skill_dependencies = []
    skill_ids = []
    
    if ver.skill_dependencies_versioned:
        skill_ids = list(ver.skill_dependencies_versioned.keys())
    elif app.skill_dependencies:
        skill_ids = [s.strip() for s in app.skill_dependencies.split(',') if s.strip()]
    
    for skill_id in skill_ids:
        skill_ver = await marketplace_skill_version_dao.get_latest_by_skill(db, skill_id)
        if skill_ver and skill_ver.package_url:
            skill_dependencies.append({
                'id': skill_id,
                'version': skill_ver.version,
                'download_url': skill_ver.package_url,
                'file_hash': skill_ver.file_hash,
            })
    
    return response_base.success(data=AppDownloadInfo(
        id=template_id,
        version=ver.version,
        package_url=ver.package_url,
        file_hash=ver.file_hash,
        file_size=ver.file_size,
        skill_dependencies=skill_dependencies if skill_dependencies else None,
    ))


# ============================================================
# 同步检查更新 API
# ============================================================

class InstalledItem(BaseModel):
    """已安装的项"""
    id: str
    version: str
    type: str  # 'skill' 或 'app'


class SyncRequest(BaseModel):
    """同步请求"""
    installed: list[InstalledItem]


class UpdateItem(BaseModel):
    """有更新的项"""
    id: str
    type: str
    current_version: str
    latest_version: str
    changelog: Optional[str] = None


class SyncResponse(BaseModel):
    """同步响应"""
    updates: list[UpdateItem]


def _is_newer_version(latest: str, current: str) -> bool:
    """简单的语义化版本比较"""
    try:
        def parse_version(v: str) -> tuple[int, ...]:
            v = v.lstrip('v')
            v = v.split('-')[0]
            return tuple(int(x) for x in v.split('.'))
        
        latest_parts = parse_version(latest)
        current_parts = parse_version(current)
        return latest_parts > current_parts
    except (ValueError, AttributeError):
        return False


@router.post('/sync', summary='公开接口：同步检查更新')
async def client_sync_installed(
    db: CurrentSession,
    request: SyncRequest,
) -> ResponseSchemaModel[SyncResponse]:
    """检查已安装的技能和应用是否有新版本"""
    updates = []
    
    for item in request.installed:
        if item.type == 'skill':
            latest = await marketplace_skill_version_dao.get_latest_by_skill(db, item.id)
            if latest and latest.version != item.version:
                if _is_newer_version(latest.version, item.version):
                    updates.append(UpdateItem(
                        id=item.id,
                        type='skill',
                        current_version=item.version,
                        latest_version=latest.version,
                        changelog=latest.changelog,
                    ))
        elif item.type == 'app':
            latest = await marketplace_template_version_dao.get_latest_by_app(db, item.id)
            if latest and latest.version != item.version:
                if _is_newer_version(latest.version, item.version):
                    updates.append(UpdateItem(
                        id=item.id,
                        type='app',
                        current_version=item.version,
                        latest_version=latest.version,
                        changelog=latest.changelog,
                    ))
    
    return response_base.success(data=SyncResponse(updates=updates))


# ============================================================
# 公开的分类列表 API
# ============================================================

@router.get('/categories', summary='公开接口：获取分类列表')
async def list_categories(
    db: CurrentSession,
) -> ResponseSchemaModel[list[GetMarketplaceCategoryDetail]]:
    """公开的分类列表接口，无需登录"""
    categories = await marketplace_category_dao.get_all(db)
    return response_base.success(data=categories)


# ============================================================
# 公开的 SOP 工作流 API
# ============================================================

@router.get('/sops', summary='公开接口：获取SOP工作流列表', dependencies=[DependsPagination])
async def list_sops(
    db: CurrentSession,
    category: Optional[str] = Query(None, description='分类筛选'),
    pricing_type: Optional[str] = Query(None, description='定价类型'),
    is_official: Optional[bool] = Query(None, description='是否官方'),
) -> ResponseSchemaModel[PageData[GetMarketplaceSopDetail]]:
    """公开的SOP列表接口，无需登录"""
    sop_select = await marketplace_sop_dao.get_select_public(
        category=category,
        pricing_type=pricing_type,
        is_official=is_official,
    )
    page_data = await paging_data(db, sop_select)
    
    for item in page_data['items']:
        latest = await marketplace_sop_version_dao.get_latest_by_sop(db, item['sop_id'])
        item['latest_version'] = latest.version if latest else None
    
    return response_base.success(data=page_data)


@router.get('/sops/{sop_id}', summary='公开接口：获取SOP详情')
async def get_sop(
    db: CurrentSession,
    sop_id: Annotated[str, Path(description='SOP ID')],
) -> ResponseSchemaModel[GetMarketplaceSopDetail]:
    """公开的SOP详情接口⌨࿠"""
    sop = await marketplace_sop_dao.get_by_id(db, sop_id)
    if not sop:
        raise errors.NotFoundError(msg='SOP不存在')
    
    sop_data = GetMarketplaceSopDetail.model_validate(sop)
    latest = await marketplace_sop_version_dao.get_latest_by_sop(db, sop_id)
    sop_data.latest_version = latest.version if latest else None
    
    return response_base.success(data=sop_data)


@router.get('/sops/{sop_id}/versions', summary='公开接口：获取SOP版本列表')
async def get_sop_versions(
    db: CurrentSession,
    sop_id: Annotated[str, Path(description='SOP ID')],
) -> ResponseSchemaModel[list[GetMarketplaceSopVersionDetail]]:
    """公开的SOP版本列表接口"""
    versions = await marketplace_sop_version_dao.get_versions_by_sop(db, sop_id)
    return response_base.success(data=versions)


@router.get('/download/sop/{sop_id}/latest', summary='公开接口：获取SOP最新版本下载信息')
async def download_sop_latest(
    db: CurrentSession,
    sop_id: Annotated[str, Path(description='SOP ID')],
) -> ResponseSchemaModel:
    """获取SOP最新版本的下载信息"""
    version = await marketplace_sop_version_dao.get_latest_by_sop(db, sop_id)
    if not version:
        raise errors.NotFoundError(msg='SOP或版本不存在')
    
    await marketplace_sop_dao.increment_download_count(db, sop_id)
    await db.commit()
    
    return response_base.success(data={
        'id': sop_id,
        'version': version.version,
        'package_url': version.package_url,
        'file_hash': version.file_hash,
        'file_size': version.file_size,
    })
