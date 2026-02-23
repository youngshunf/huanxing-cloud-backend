"""订阅升级/降级服务 - 管理 API Key 过期策略
@author Ysf
"""

from datetime import timedelta

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.llm.enums import ApiKeyStatus
from backend.app.llm.model.user_api_key import UserApiKey
from backend.app.user_tier.model import UserSubscription
from backend.common.log import log
from backend.utils.timezone import timezone


class SubscriptionService:
    """订阅升级/降级服务"""

    @staticmethod
    async def upgrade_subscription(
        db: AsyncSession,
        user_id: int,
        new_tier: str,
        subscription_type: str = 'monthly',
    ) -> None:
        """
        升级用户订阅，并自动续期/激活用户的 API Key

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param new_tier: 新的订阅等级 (basic/pro/enterprise)
        :param subscription_type: 订阅类型 (monthly/yearly)
        """
        now = timezone.now()

        # 1. 更新订阅信息
        sub_stmt = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await db.execute(sub_stmt)
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.tier = new_tier
            subscription.subscription_type = subscription_type
            subscription.status = 'active'
            subscription.subscription_start_date = now
            if subscription_type == 'yearly':
                subscription.subscription_end_date = now + timedelta(days=365)
            else:
                subscription.subscription_end_date = now + timedelta(days=30)
            await db.flush()

        # 2. 处理用户的所有 API Key
        key_stmt = select(UserApiKey).where(
            and_(
                UserApiKey.user_id == user_id,
                UserApiKey.status.in_([ApiKeyStatus.ACTIVE, ApiKeyStatus.EXPIRED]),
            )
        )
        key_result = await db.execute(key_stmt)
        keys = key_result.scalars().all()

        # 计算新的过期时间：付费用户设为订阅结束时间
        new_expires_at = subscription.subscription_end_date if subscription else None

        active_count = 0
        reactivated_count = 0

        for key in keys:
            if key.status == ApiKeyStatus.ACTIVE:
                # 活跃 Key：移除过期时间或设为订阅结束时间
                key.expires_at = new_expires_at
                active_count += 1
            elif key.status == ApiKeyStatus.EXPIRED:
                # 过期 Key：重新激活
                key.status = ApiKeyStatus.ACTIVE
                key.expires_at = new_expires_at
                reactivated_count += 1

        await db.flush()

        log.info(
            f'[Subscription] 用户 {user_id} 升级到 {new_tier}，'
            f'更新 {active_count} 个活跃 Key，重新激活 {reactivated_count} 个过期 Key'
        )

    @staticmethod
    async def downgrade_to_free(db: AsyncSession, user_id: int) -> None:
        """
        降级用户到免费版，所有活跃 API Key 设置 7 天过期

        :param db: 数据库会话
        :param user_id: 用户 ID
        """
        now = timezone.now()
        expires_at = now + timedelta(days=7)

        # 1. 更新订阅为免费版
        sub_stmt = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await db.execute(sub_stmt)
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.tier = 'free'
            subscription.subscription_type = 'monthly'
            subscription.subscription_end_date = None
            subscription.status = 'active'
            await db.flush()

        # 2. 所有活跃 Key 设置 7 天过期
        update_stmt = (
            update(UserApiKey)
            .where(
                and_(
                    UserApiKey.user_id == user_id,
                    UserApiKey.status == ApiKeyStatus.ACTIVE,
                )
            )
            .values(expires_at=expires_at)
        )
        result = await db.execute(update_stmt)
        updated_count = result.rowcount

        log.info(
            f'[Subscription] 用户 {user_id} 降级到免费版，'
            f'{updated_count} 个活跃 Key 设置 7 天后过期'
        )


subscription_service = SubscriptionService()
