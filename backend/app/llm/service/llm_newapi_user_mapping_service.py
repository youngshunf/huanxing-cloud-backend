"""唤星用户与 new-api 用户映射服务

基础 CRUD（代码生成器生成）+ new-api 集成业务逻辑：
- ensure_newapi_user: 登录时自动创建 new-api 用户 + token
- sync_quota: 订阅变更时同步 quota
- get_quota_info / get_usage_summary / get_usage_detail: 用量查询

双库架构：
- db (唤星库): llm_newapi_user_mapping 映射表
- newapi_db (new-api 库): users, tokens, logs 等 new-api 原生表
"""

import time
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.llm.crud.crud_llm_newapi_user_mapping import llm_newapi_user_mapping_dao, newapi_direct_dao
from backend.app.llm.model import LlmNewapiUserMapping
from backend.app.llm.schema.llm_newapi_user_mapping import (
    CreateLlmNewapiUserMappingParam,
    DeleteLlmNewapiUserMappingParam,
    NewApiMappingInfo,
    NewApiQuotaInfo,
    NewApiUsageDetail,
    NewApiUsageDetailItem,
    NewApiUsageSummary,
    NewApiUsageSummaryItem,
    UpdateLlmNewapiUserMappingParam,
)
from backend.common.exception import errors
from backend.common.log import log
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.database.db import newapi_async_db_session


def credits_to_quota(credits: int) -> int:
    """唤星积分 → new-api quota"""
    return credits * settings.NEWAPI_CREDITS_TO_QUOTA_RATE


# 各套餐默认 quota（当 subscription_tier.features 中未配置 newapi_quota 时使用）
DEFAULT_TIER_QUOTA = {
    'free': credits_to_quota(100),        # 微星 100 积分
    'pro': credits_to_quota(1_000),       # 明星 1,000 积分
    'advanced': credits_to_quota(5_000),  # 恒星 5,000 积分
    'flagship': credits_to_quota(20_000), # 超新星 20,000 积分
}


async def _get_newapi_session() -> AsyncSession:
    """获取 new-api 数据库会话"""
    return newapi_async_db_session()


class LlmNewapiUserMappingService:

    # ========== 基础 CRUD（唤星库）==========

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> LlmNewapiUserMapping:
        llm_newapi_user_mapping = await llm_newapi_user_mapping_dao.get(db, pk)
        if not llm_newapi_user_mapping:
            raise errors.NotFoundError(msg='唤星用户与 new-api 用户映射不存在')
        return llm_newapi_user_mapping

    @staticmethod
    async def get_list(db: AsyncSession, **kwargs) -> dict[str, Any]:
        llm_newapi_user_mapping_select = await llm_newapi_user_mapping_dao.get_select()
        return await paging_data(db, llm_newapi_user_mapping_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[LlmNewapiUserMapping]:
        return await llm_newapi_user_mapping_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateLlmNewapiUserMappingParam, **kwargs) -> None:
        await llm_newapi_user_mapping_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateLlmNewapiUserMappingParam, **kwargs) -> int:
        return await llm_newapi_user_mapping_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteLlmNewapiUserMappingParam) -> int:
        return await llm_newapi_user_mapping_dao.delete(db, obj.pks)

    # ========== new-api 集成业务逻辑（双库）==========

    @staticmethod
    async def ensure_newapi_user(
        db: AsyncSession,
        huanxing_user_id: int,
        *,
        username: str = '',
        nickname: str = '',
        app_code: str = 'huanxing',
        initial_quota: int | None = None,
    ) -> NewApiMappingInfo:
        """
        确保唤星用户在 new-api 中有对应的用户和 token。
        已存在映射则直接返回，否则创建。

        db: 唤星库 session（读写映射表）
        new-api 库通过内部 session 操作
        """
        existing = await llm_newapi_user_mapping_dao.get_by_user(db, huanxing_user_id, app_code)
        if existing:
            return NewApiMappingInfo(
                huanxing_user_id=existing.huanxing_user_id,
                newapi_user_id=existing.newapi_user_id,
                newapi_token_key=existing.newapi_token_key,
                app_code=existing.app_code,
                status=existing.status,
            )

        quota = initial_quota or DEFAULT_TIER_QUOTA.get('free', 50_000)
        newapi_username = username or f'hx_{huanxing_user_id}'
        display = nickname or newapi_username

        # 操作 new-api 独立数据库
        async with newapi_async_db_session.begin() as newapi_db:
            # 1. 创建 new-api 用户
            newapi_user_id = await newapi_direct_dao.create_newapi_user(
                newapi_db, username=newapi_username, display_name=display, quota=quota,
            )

            # 2. 生成 token key 并创建 token（无限额度，由 users.quota 控制）
            token_key = newapi_direct_dao.generate_token_key()
            newapi_token_id = await newapi_direct_dao.create_newapi_token(
                newapi_db, user_id=newapi_user_id, token_key=token_key,
                name=f'{app_code} 默认 Key',
            )

        # 3. 创建映射记录（唤星库）
        mapping = LlmNewapiUserMapping(
            huanxing_user_id=huanxing_user_id,
            newapi_user_id=newapi_user_id,
            newapi_token_key=token_key,
            newapi_token_id=newapi_token_id,
            app_code=app_code,
            status='active',
        )
        db.add(mapping)
        await db.flush()

        log.info(
            f'[NewApi] 为唤星用户 {huanxing_user_id} 创建 new-api 用户 {newapi_user_id}，'
            f'token_id={newapi_token_id}，quota={quota}'
        )

        return NewApiMappingInfo(
            huanxing_user_id=huanxing_user_id,
            newapi_user_id=newapi_user_id,
            newapi_token_key=token_key,
            app_code=app_code,
            status='active',
        )

    @staticmethod
    async def sync_quota(
        db: AsyncSession,
        huanxing_user_id: int,
        new_quota: int,
        *,
        app_code: str = 'huanxing',
    ) -> None:
        """同步 quota 到 new-api（订阅变更时调用）"""
        mapping = await llm_newapi_user_mapping_dao.get_by_user(db, huanxing_user_id, app_code)
        if not mapping:
            log.warning(f'[NewApi] 用户 {huanxing_user_id} 无 new-api 映射，跳过 quota 同步')
            return

        async with newapi_async_db_session.begin() as newapi_db:
            await newapi_direct_dao.update_newapi_quota(
                newapi_db, newapi_user_id=mapping.newapi_user_id, new_quota=new_quota,
            )
        log.info(f'[NewApi] 用户 {huanxing_user_id} quota 同步到 {new_quota}')

    @staticmethod
    async def get_quota_info(
        db: AsyncSession,
        huanxing_user_id: int,
        *,
        app_code: str = 'huanxing',
    ) -> NewApiQuotaInfo:
        """查询用户的 new-api 额度信息"""
        mapping = await llm_newapi_user_mapping_dao.get_by_user(db, huanxing_user_id, app_code)
        if not mapping:
            raise errors.NotFoundError(msg='用户未关联 LLM 服务')

        async with newapi_async_db_session() as newapi_db:
            user_quota = await newapi_direct_dao.get_newapi_user_quota(newapi_db, mapping.newapi_user_id)
            if not user_quota:
                raise errors.NotFoundError(msg='LLM 用户信息不存在')
            token_remain = await newapi_direct_dao.get_token_remain_quota(newapi_db, mapping.newapi_token_id)

        return NewApiQuotaInfo(
            total_quota=user_quota['quota'],
            used_quota=user_quota['used_quota'],
            remain_quota=token_remain or 0,
            request_count=user_quota['request_count'],
        )

    @staticmethod
    async def get_usage_summary(
        db: AsyncSession,
        huanxing_user_id: int,
        start_time: int,
        end_time: int,
        *,
        app_code: str = 'huanxing',
    ) -> NewApiUsageSummary:
        """查询用量统计概览"""
        mapping = await llm_newapi_user_mapping_dao.get_by_user(db, huanxing_user_id, app_code)
        if not mapping:
            raise errors.NotFoundError(msg='用户未关联 LLM 服务')

        async with newapi_async_db_session() as newapi_db:
            rows = await newapi_direct_dao.get_usage_summary(
                newapi_db, mapping.newapi_user_id, start_time, end_time,
            )
        items = [NewApiUsageSummaryItem(**row) for row in rows]

        return NewApiUsageSummary(
            items=items,
            total_prompt_tokens=sum(i.prompt_tokens for i in items),
            total_completion_tokens=sum(i.completion_tokens for i in items),
            total_quota=sum(i.quota for i in items),
            total_requests=sum(i.request_count for i in items),
            period_start=start_time,
            period_end=end_time,
        )

    @staticmethod
    async def get_usage_detail(
        db: AsyncSession,
        huanxing_user_id: int,
        start_time: int,
        end_time: int,
        *,
        model_name: str | None = None,
        limit: int = 50,
        offset: int = 0,
        app_code: str = 'huanxing',
    ) -> NewApiUsageDetail:
        """查询用量明细"""
        mapping = await llm_newapi_user_mapping_dao.get_by_user(db, huanxing_user_id, app_code)
        if not mapping:
            raise errors.NotFoundError(msg='用户未关联 LLM 服务')

        async with newapi_async_db_session() as newapi_db:
            records, total = await newapi_direct_dao.get_usage_detail(
                newapi_db, mapping.newapi_user_id, start_time, end_time,
                model_name=model_name, limit=limit, offset=offset,
            )
        return NewApiUsageDetail(items=[NewApiUsageDetailItem(**r) for r in records], total=total)

    @staticmethod
    async def get_api_key(
        db: AsyncSession,
        huanxing_user_id: int,
        *,
        app_code: str = 'huanxing',
    ) -> str:
        """获取用户的 new-api API Key"""
        mapping = await llm_newapi_user_mapping_dao.get_by_user(db, huanxing_user_id, app_code)
        if not mapping:
            raise errors.NotFoundError(msg='用户未关联 LLM 服务')
        return f'sk-{mapping.newapi_token_key}'

    @staticmethod
    def tier_to_quota(tier_name: str, features: dict | None = None) -> int:
        """将订阅等级转换为 new-api quota"""
        if features and 'newapi_quota' in features:
            return int(features['newapi_quota'])
        return DEFAULT_TIER_QUOTA.get(tier_name, DEFAULT_TIER_QUOTA['free'])


llm_newapi_user_mapping_service: LlmNewapiUserMappingService = LlmNewapiUserMappingService()
