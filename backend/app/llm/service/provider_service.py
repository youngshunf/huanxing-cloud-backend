"""模型供应商 Service"""

import logging

from typing import Any

import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.llm.core.encryption import key_encryption
from backend.app.llm.crud.crud_model_config import model_config_dao
from backend.app.llm.model.model_config import ModelConfig
from backend.app.llm.crud.crud_provider import provider_dao
from backend.app.llm.model.provider import ModelProvider
from backend.app.llm.schema.provider import (
    CreateProviderParam,
    GetProviderDetail,
    UpdateProviderParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data

log = logging.getLogger(__name__)


def _infer_model_meta(model_id: str, owned_by: str | None = None) -> dict[str, Any]:
    """根据模型名称推断类型和能力参数"""
    mid = model_id.lower()

    # Embedding
    if 'embed' in mid:
        return dict(model_type='EMBEDDING', supports_vision=False, supports_tools=False,
                    max_tokens=0, max_context_length=8192, supports_streaming=False)
    # Image
    if 'dall-e' in mid or 'image' in mid:
        return dict(model_type='IMAGE', supports_vision=False, supports_tools=False,
                    max_tokens=0, max_context_length=0, supports_streaming=False)
    # TTS
    if mid.startswith('tts') or 'whisper' in mid:
        t = 'TTS' if mid.startswith('tts') else 'STT'
        return dict(model_type=t, supports_vision=False, supports_tools=False,
                    max_tokens=0, max_context_length=0, supports_streaming=False)

    # Reasoning models
    if any(k in mid for k in ('o1', 'o3', 'o4', 'reasoning', 'think')):
        return dict(model_type='REASONING', supports_vision=False, supports_tools=True,
                    max_tokens=32768, max_context_length=200000, supports_streaming=True)

    # Claude
    if 'claude' in mid:
        is_vision = True
        supports_tools = True
        if 'opus' in mid:
            return dict(model_type='REASONING', supports_vision=is_vision, supports_tools=supports_tools,
                        max_tokens=32768, max_context_length=200000, supports_streaming=True)
        if 'haiku' in mid:
            return dict(model_type='TEXT', supports_vision=is_vision, supports_tools=supports_tools,
                        max_tokens=8192, max_context_length=200000, supports_streaming=True)
        # sonnet / default
        return dict(model_type='TEXT', supports_vision=is_vision, supports_tools=supports_tools,
                    max_tokens=16384, max_context_length=200000, supports_streaming=True)

    # GPT-5.x / codex
    if any(k in mid for k in ('gpt-5', 'codex')):
        return dict(model_type='REASONING', supports_vision=False, supports_tools=True,
                    max_tokens=32768, max_context_length=256000, supports_streaming=True)

    # GPT-4o / GPT-4.1
    if 'gpt-4o' in mid:
        return dict(model_type='TEXT', supports_vision=True, supports_tools=True,
                    max_tokens=16384, max_context_length=128000, supports_streaming=True)
    if 'gpt-4.1' in mid or 'gpt-4-1' in mid:
        return dict(model_type='REASONING', supports_vision=False, supports_tools=True,
                    max_tokens=32768, max_context_length=1047576, supports_streaming=True)

    # Gemini
    if 'gemini' in mid:
        return dict(model_type='TEXT', supports_vision=True, supports_tools=True,
                    max_tokens=8192, max_context_length=128000, supports_streaming=True)

    # DeepSeek
    if 'deepseek' in mid:
        return dict(model_type='REASONING', supports_vision=False, supports_tools=True,
                    max_tokens=8192, max_context_length=64000, supports_streaming=True)

    # Grok
    if 'grok' in mid:
        return dict(model_type='TEXT', supports_vision=False, supports_tools=True,
                    max_tokens=8192, max_context_length=128000, supports_streaming=True)

    # Default: text model
    return dict(model_type='TEXT', supports_vision=False, supports_tools=True,
                max_tokens=4096, max_context_length=8192, supports_streaming=True)


class ProviderService:
    """模型供应商服务"""

    @staticmethod
    async def get(db: AsyncSession, pk: int) -> ModelProvider:
        """获取供应商详情"""
        provider = await provider_dao.get(db, pk)
        if not provider:
            raise errors.NotFoundError(msg='供应商不存在')
        return provider

    @staticmethod
    async def get_detail(db: AsyncSession, pk: int) -> GetProviderDetail:
        """获取供应商详情（带 API Key 状态）"""
        provider = await provider_dao.get(db, pk)
        if not provider:
            raise errors.NotFoundError(msg='供应商不存在')
        return GetProviderDetail.from_orm_with_key_check(provider)

    @staticmethod
    async def get_list(
        db: AsyncSession,
        *,
        name: str | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any]:
        """获取供应商列表（分页）"""
        stmt = await provider_dao.get_list(name=name, enabled=enabled)
        page_data = await paging_data(db, stmt)
        return page_data

    @staticmethod
    async def get_all_enabled(db: AsyncSession) -> list[ModelProvider]:
        """获取所有启用的供应商"""
        return await provider_dao.get_all_enabled(db)

    @staticmethod
    async def create(db: AsyncSession, obj: CreateProviderParam) -> None:
        """创建供应商"""
        existing = await provider_dao.get_by_name(db, obj.name)
        if existing:
            raise errors.ForbiddenError(msg='供应商名称已存在')
        api_key_encrypted = None
        if obj.api_key:
            api_key_encrypted = key_encryption.encrypt(obj.api_key)
        await provider_dao.create(db, obj, api_key_encrypted)

    @staticmethod
    async def update(db: AsyncSession, pk: int, obj: UpdateProviderParam) -> int:
        """更新供应商"""
        provider = await provider_dao.get(db, pk)
        if not provider:
            raise errors.NotFoundError(msg='供应商不存在')
        if obj.name and obj.name != provider.name:
            existing = await provider_dao.get_by_name(db, obj.name)
            if existing:
                raise errors.ForbiddenError(msg='供应商名称已存在')
        api_key_encrypted = None
        if obj.api_key:
            api_key_encrypted = key_encryption.encrypt(obj.api_key)
        return await provider_dao.update(db, pk, obj, api_key_encrypted)

    @staticmethod
    async def delete(db: AsyncSession, pk: int) -> int:
        """删除供应商"""
        provider = await provider_dao.get(db, pk)
        if not provider:
            raise errors.NotFoundError(msg='供应商不存在')
        return await provider_dao.delete(db, pk)

    @staticmethod
    async def sync_models(db: AsyncSession, pk: int) -> dict[str, Any]:
        """
        一键同步供应商模型列表

        调用 供应商 base_url/v1/models 获取模型列表，
        自动推断模型类型和能力参数，写入 llm_model_config 表。
        已存在的模型跳过，新模型自动创建。

        Returns:
            dict: {created: int, skipped: int, failed: int, models: [...]}
        """
        provider = await provider_dao.get(db, pk)
        if not provider:
            raise errors.NotFoundError(msg='供应商不存在')

        if not provider.api_base_url:
            raise errors.ForbiddenError(msg='供应商未配置 API Base URL，无法同步模型')

        # 解密 API Key
        api_key = None
        if provider.api_key_encrypted:
            try:
                api_key = key_encryption.decrypt(provider.api_key_encrypted)
            except Exception:
                log.warning(f'供应商 {provider.name} API Key 解密失败')

        # 请求 /v1/models
        base_url = provider.api_base_url.rstrip('/')
        models_url = f'{base_url}/v1/models'

        headers = {'Accept': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        try:
            async with httpx.AsyncClient(timeout=30, verify=False) as client:
                resp = await client.get(models_url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            raise errors.RequestError(
                msg=f'获取模型列表失败: HTTP {e.response.status_code}，请检查供应商 API Base URL 是否正确'
            )
        except httpx.RequestError as e:
            raise errors.RequestError(msg=f'请求模型列表失败: {e}，请检查供应商 API Base URL 是否可访问')
        except Exception as e:
            raise errors.ServerError(msg=f'解析模型列表失败: {e}')

        # 解析 OpenAI 格式的 /v1/models 响应
        model_list = data.get('data', [])
        if not model_list:
            raise errors.ForbiddenError(msg='供应商返回的模型列表为空')

        created = 0
        skipped = 0
        failed = 0
        created_models = []

        for item in model_list:
            model_id = item.get('id', '').strip()
            if not model_id:
                continue

            owned_by = item.get('owned_by', '')

            # 检查是否已存在
            try:
                existing = await model_config_dao.get_by_provider_and_name(db, pk, model_id)
                if existing:
                    skipped += 1
                    continue
            except Exception:
                # 如果查询出错（如事务异常），先回滚再继续
                await db.rollback()
                skipped += 1
                continue

            # 推断模型元信息
            meta = _infer_model_meta(model_id, owned_by)

            try:
                new_model = ModelConfig(
                    provider_id=pk,
                    model_name=model_id,
                    display_name=model_id,
                    model_type=meta['model_type'],
                    max_tokens=meta['max_tokens'],
                    max_context_length=meta['max_context_length'],
                    supports_streaming=meta['supports_streaming'],
                    supports_tools=meta['supports_tools'],
                    supports_vision=meta['supports_vision'],
                    enabled=True,
                    visible=True,
                )
                db.add(new_model)
                await db.flush()
                created += 1
                created_models.append(model_id)
            except Exception as e:
                log.warning(f'创建模型 {model_id} 失败: {e}')
                await db.rollback()
                failed += 1

        # 最终提交所有成功的记录
        try:
            await db.commit()
        except Exception:
            await db.rollback()

        return {
            'total': len(model_list),
            'created': created,
            'skipped': skipped,
            'failed': failed,
            'models': created_models,
        }


provider_service = ProviderService()
