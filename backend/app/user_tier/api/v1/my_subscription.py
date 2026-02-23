"""用户订阅 API - 面向前端用户（JWT 认证）
@author Ysf
"""

from typing import Annotated
from datetime import timedelta
import uuid

from fastapi import APIRouter, Header, Query, Body, Request
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

from backend.app.user_tier.service.credit_service import credit_service
from backend.app.user_tier.crud.crud_subscription_tier import subscription_tier_dao
from backend.app.user_tier.crud.crud_credit_package import credit_package_dao
from backend.common.response.response_schema import ResponseSchemaModel, ResponseModel, response_base
from backend.common.log import log
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.utils.timezone import timezone

router = APIRouter()


# ==================== Response Schemas ====================


class CreditBalanceItem(BaseModel):
    """积分余额项"""
    id: int
    credit_type: str
    original_amount: Decimal
    used_amount: Decimal
    remaining_amount: Decimal
    expires_at: datetime | None = None
    granted_at: datetime
    source_type: str
    description: str | None = None


class SubscriptionInfoResponse(BaseModel):
    """订阅信息响应"""
    user_id: int
    tier: str
    tier_display_name: str | None = None
    subscription_type: str = 'monthly'  # monthly/yearly
    monthly_credits: Decimal
    current_credits: Decimal
    used_credits: Decimal
    purchased_credits: Decimal
    monthly_remaining: Decimal | None = None
    bonus_remaining: Decimal | None = None
    billing_cycle_start: datetime
    billing_cycle_end: datetime
    subscription_start_date: datetime | None = None
    subscription_end_date: datetime | None = None
    next_grant_date: datetime | None = None  # 年度订阅下次赠送时间
    status: str
    balances: list[CreditBalanceItem] = []


class SubscriptionTierItem(BaseModel):
    """订阅等级项"""
    id: int
    tier_name: str
    display_name: str
    monthly_credits: Decimal
    monthly_price: Decimal
    yearly_price: Decimal | None = None
    yearly_discount: Decimal | None = None
    features: dict | None = None


class CreditPackageItem(BaseModel):
    """积分包项"""
    id: int
    package_name: str
    credits: Decimal
    price: Decimal
    bonus_credits: Decimal
    description: str | None = None


class UpgradeSubscriptionRequest(BaseModel):
    """升级订阅请求"""
    tier_name: str = Field(description='目标订阅等级')
    subscription_type: str = Field(default='monthly', description='订阅类型 (monthly/yearly)')


class CalculateUpgradePriceRequest(BaseModel):
    """计算升级价格请求"""
    tier_name: str = Field(description='目标订阅等级')
    subscription_type: str = Field(default='monthly', description='订阅类型 (monthly/yearly)')


class UpgradePriceResult(BaseModel):
    """升级价格计算结果"""
    can_upgrade: bool = Field(description='是否可以升级')
    message: str = Field(description='提示信息')
    target_tier: str = Field(description='目标等级')
    target_tier_display: str = Field(description='目标等级显示名')
    subscription_type: str = Field(description='订阅类型')
    original_price: Decimal = Field(description='原价')
    remaining_value: Decimal = Field(description='当前订阅剩余价值')
    final_price: Decimal = Field(description='实际支付价格')
    remaining_days: int = Field(description='当前订阅剩余天数')
    current_tier: str = Field(description='当前等级')
    current_subscription_type: str = Field(description='当前订阅类型')


class PurchaseCreditsRequest(BaseModel):
    """购买积分包请求"""
    package_id: int = Field(description='积分包 ID')


class PaymentResult(BaseModel):
    """支付结果"""
    success: bool
    order_id: str
    message: str
    new_credits: Decimal | None = None
    new_tier: str | None = None


# ==================== APIs ====================


@router.get(
    '/info',
    summary='获取当前用户订阅信息',
    description='获取当前登录用户的订阅和积分信息',
    dependencies=[DependsJwtAuth],
)
async def get_my_subscription_info(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[SubscriptionInfoResponse]:
    """获取订阅信息"""
    user_id = request.user.id
    app_code = request.state.app_code

    # 获取完整的积分信息（包含 balances）
    info = await credit_service.get_user_credits_info(db, user_id, app_code)
    
    # 转换 balances 为 CreditBalanceItem
    balances = [
        CreditBalanceItem(
            id=b['id'],
            credit_type=b['credit_type'],
            original_amount=Decimal(str(b['original_amount'])),
            used_amount=Decimal(str(b['used_amount'])),
            remaining_amount=Decimal(str(b['remaining_amount'])),
            expires_at=datetime.fromisoformat(b['expires_at']) if b['expires_at'] else None,
            granted_at=datetime.fromisoformat(b['granted_at']),
            source_type=b['source_type'],
            description=b['description'],
        )
        for b in info.get('balances', [])
    ]
    
    data = SubscriptionInfoResponse(
        user_id=info['user_id'],
        tier=info['tier'],
        tier_display_name=info['tier_display_name'],
        subscription_type=info.get('subscription_type', 'monthly'),
        monthly_credits=Decimal(str(info['monthly_credits'])),
        current_credits=Decimal(str(info['current_credits'])),
        used_credits=Decimal(str(info['used_credits'])),
        purchased_credits=Decimal(str(info['purchased_credits'])),
        monthly_remaining=Decimal(str(info.get('monthly_remaining', 0))),
        bonus_remaining=Decimal(str(info.get('bonus_remaining', 0))),
        billing_cycle_start=datetime.fromisoformat(info['billing_cycle_start']),
        billing_cycle_end=datetime.fromisoformat(info['billing_cycle_end']),
        subscription_start_date=datetime.fromisoformat(info['subscription_start_date']) if info.get('subscription_start_date') else None,
        subscription_end_date=datetime.fromisoformat(info['subscription_end_date']) if info.get('subscription_end_date') else None,
        next_grant_date=datetime.fromisoformat(info['next_grant_date']) if info.get('next_grant_date') else None,
        status=info['status'],
        balances=balances,
    )
    
    return response_base.success(data=data)


@router.get(
    '/balances/history',
    summary='获取历史积分记录',
    description='获取已过期的积分余额记录',
    dependencies=[DependsJwtAuth],
)
async def get_credit_balance_history(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[list[CreditBalanceItem]]:
    """获取历史积分记录"""
    user_id = request.user.id
    app_code = request.state.app_code

    # 获取已过期的积分记录
    expired_balances = await credit_service.get_user_expired_balances(db, user_id, app_code)
    
    items = [
        CreditBalanceItem(
            id=b.id,
            credit_type=b.credit_type,
            original_amount=b.original_amount,
            used_amount=b.used_amount,
            remaining_amount=b.remaining_amount,
            expires_at=b.expires_at,
            granted_at=b.granted_at,
            source_type=b.source_type,
            description=b.description,
        )
        for b in expired_balances
    ]
    
    return response_base.success(data=items)


@router.get(
    '/tiers',
    summary='获取订阅等级列表（公开）',
    description='获取所有可用的订阅等级，无需登录',
)
async def get_subscription_tiers(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[list[SubscriptionTierItem]]:
    """获取订阅等级列表"""
    from sqlalchemy import select
    from backend.app.user_tier.model import SubscriptionTier

    app_code = request.state.app_code
    stmt = (
        select(SubscriptionTier)
        .where(SubscriptionTier.enabled == True, SubscriptionTier.app_code == app_code)
        .order_by(SubscriptionTier.sort_order)
    )
    result = await db.execute(stmt)
    tiers = result.scalars().all()
    
    items = [
        SubscriptionTierItem(
            id=t.id,
            tier_name=t.tier_name,
            display_name=t.display_name,
            monthly_credits=t.monthly_credits,
            monthly_price=t.monthly_price,
            yearly_price=t.yearly_price,
            yearly_discount=t.yearly_discount,
            features=t.features,
        )
        for t in tiers
    ]
    
    return response_base.success(data=items)


@router.get(
    '/packages',
    summary='获取积分包列表（公开）',
    description='获取所有可购买的积分包，无需登录',
)
async def get_credit_packages(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[list[CreditPackageItem]]:
    """获取积分包列表"""
    from sqlalchemy import select
    from backend.app.user_tier.model import CreditPackage

    app_code = request.state.app_code
    stmt = (
        select(CreditPackage)
        .where(CreditPackage.enabled == True, CreditPackage.app_code == app_code)
        .order_by(CreditPackage.sort_order)
    )
    result = await db.execute(stmt)
    packages = result.scalars().all()
    
    items = [
        CreditPackageItem(
            id=p.id,
            package_name=p.package_name,
            credits=p.credits,
            price=p.price,
            bonus_credits=p.bonus_credits,
            description=p.description,
        )
        for p in packages
    ]
    
    return response_base.success(data=items)


def _calculate_remaining_value(
    current_price: Decimal,
    subscription_end_date: datetime | None,
    subscription_type: str,
) -> tuple[Decimal, int]:
    """
    计算当前订阅的剩余价值
    
    :return: (剩余价值, 剩余天数)
    """
    if not subscription_end_date or current_price <= 0:
        return Decimal('0'), 0
    
    now = timezone.now()
    if now >= subscription_end_date:
        return Decimal('0'), 0
    
    remaining_days = (subscription_end_date - now).days
    total_days = 365 if subscription_type == 'yearly' else 30
    
    # 计算剩余价值 = 当前价格 * (剩余天数 / 总天数)
    remaining_value = current_price * Decimal(str(remaining_days)) / Decimal(str(total_days))
    # 四舍五入到分
    remaining_value = remaining_value.quantize(Decimal('0.01'))
    
    return remaining_value, remaining_days


@router.post(
    '/upgrade/calculate',
    summary='计算升级价格',
    description='计算升级到目标等级需要支付的价格（折算剩余价值）',
    dependencies=[DependsJwtAuth],
)
async def calculate_upgrade_price(
    request: Request,
    db: CurrentSession,
    body: CalculateUpgradePriceRequest,
) -> ResponseSchemaModel[UpgradePriceResult]:
    """计算升级价格"""
    user_id = request.user.id
    app_code = request.state.app_code

    # 获取目标等级
    target_tier = await subscription_tier_dao.select_model_by_column(db, tier_name=body.tier_name, enabled=True, app_code=app_code)
    if not target_tier:
        return response_base.success(data=UpgradePriceResult(
            can_upgrade=False,
            message=f'订阅等级 {body.tier_name} 不存在或未启用',
            target_tier=body.tier_name,
            target_tier_display=body.tier_name,
            subscription_type=body.subscription_type,
            original_price=Decimal('0'),
            remaining_value=Decimal('0'),
            final_price=Decimal('0'),
            remaining_days=0,
            current_tier='',
            current_subscription_type='',
        ))
    
    # 获取用户当前订阅
    subscription = await credit_service.get_or_create_subscription(db, user_id, app_code)
    current_subscription_type = getattr(subscription, 'subscription_type', 'monthly') or 'monthly'

    # 获取当前等级配置
    current_tier_config = await subscription_tier_dao.select_model_by_column(db, tier_name=subscription.tier, app_code=app_code)
    current_price = Decimal('0')
    if current_tier_config:
        if current_subscription_type == 'yearly' and current_tier_config.yearly_price:
            current_price = current_tier_config.yearly_price
        else:
            current_price = current_tier_config.monthly_price or Decimal('0')
    
    # 检查是否已经是该等级和订阅类型
    if subscription.tier == body.tier_name and current_subscription_type == body.subscription_type:
        return response_base.success(data=UpgradePriceResult(
            can_upgrade=False,
            message=f'您已经是 {target_tier.display_name} {"年度" if body.subscription_type == "yearly" else "月度"}用户',
            target_tier=body.tier_name,
            target_tier_display=target_tier.display_name,
            subscription_type=body.subscription_type,
            original_price=Decimal('0'),
            remaining_value=Decimal('0'),
            final_price=Decimal('0'),
            remaining_days=0,
            current_tier=subscription.tier,
            current_subscription_type=current_subscription_type,
        ))
    
    # 年度订阅用户不能降级到月度
    if current_subscription_type == 'yearly' and body.subscription_type == 'monthly':
        return response_base.success(data=UpgradePriceResult(
            can_upgrade=False,
            message='年度订阅用户不能切换为月度订阅',
            target_tier=body.tier_name,
            target_tier_display=target_tier.display_name,
            subscription_type=body.subscription_type,
            original_price=Decimal('0'),
            remaining_value=Decimal('0'),
            final_price=Decimal('0'),
            remaining_days=0,
            current_tier=subscription.tier,
            current_subscription_type=current_subscription_type,
        ))
    
    # 检查是否降级
    target_price_monthly = target_tier.monthly_price or Decimal('0')
    current_price_monthly = current_tier_config.monthly_price if current_tier_config else Decimal('0')
    if target_price_monthly < current_price_monthly:
        return response_base.success(data=UpgradePriceResult(
            can_upgrade=False,
            message='不支持降级订阅',
            target_tier=body.tier_name,
            target_tier_display=target_tier.display_name,
            subscription_type=body.subscription_type,
            original_price=Decimal('0'),
            remaining_value=Decimal('0'),
            final_price=Decimal('0'),
            remaining_days=0,
            current_tier=subscription.tier,
            current_subscription_type=current_subscription_type,
        ))
    
    # 年度订阅需要配置年费价格
    if body.subscription_type == 'yearly' and not target_tier.yearly_price:
        return response_base.success(data=UpgradePriceResult(
            can_upgrade=False,
            message=f'{target_tier.display_name} 暂不支持年度订阅',
            target_tier=body.tier_name,
            target_tier_display=target_tier.display_name,
            subscription_type=body.subscription_type,
            original_price=Decimal('0'),
            remaining_value=Decimal('0'),
            final_price=Decimal('0'),
            remaining_days=0,
            current_tier=subscription.tier,
            current_subscription_type=current_subscription_type,
        ))
    
    # 计算目标价格
    if body.subscription_type == 'yearly':
        original_price = target_tier.yearly_price
    else:
        original_price = target_tier.monthly_price
    
    # 计算当前订阅剩余价值
    subscription_end = getattr(subscription, 'subscription_end_date', None)
    remaining_value, remaining_days = _calculate_remaining_value(
        current_price,
        subscription_end,
        current_subscription_type,
    )
    
    # 计算最终价格
    final_price = original_price - remaining_value
    # 最低支付 0 元
    if final_price < 0:
        final_price = Decimal('0')
    
    return response_base.success(data=UpgradePriceResult(
        can_upgrade=True,
        message='',
        target_tier=body.tier_name,
        target_tier_display=target_tier.display_name,
        subscription_type=body.subscription_type,
        original_price=original_price,
        remaining_value=remaining_value,
        final_price=final_price,
        remaining_days=remaining_days,
        current_tier=subscription.tier,
        current_subscription_type=current_subscription_type,
    ))


@router.post(
    '/upgrade',
    summary='升级订阅（模拟支付）',
    description='升级到更高级的订阅等级，使用模拟支付，按比例折算剩余价值',
    dependencies=[DependsJwtAuth],
)
async def upgrade_subscription(
    request: Request,
    db: CurrentSessionTransaction,
    body: UpgradeSubscriptionRequest,
) -> ResponseSchemaModel[PaymentResult]:
    """升级订阅"""
    user_id = request.user.id
    app_code = request.state.app_code

    # 获取目标等级
    target_tier = await subscription_tier_dao.select_model_by_column(db, tier_name=body.tier_name, enabled=True, app_code=app_code)
    if not target_tier:
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message=f'订阅等级 {body.tier_name} 不存在或未启用',
        ))
    
    # 获取用户当前订阅
    subscription = await credit_service.get_or_create_subscription(db, user_id, app_code)
    current_subscription_type = getattr(subscription, 'subscription_type', 'monthly') or 'monthly'

    # 获取当前等级配置
    current_tier_config = await subscription_tier_dao.select_model_by_column(db, tier_name=subscription.tier, app_code=app_code)
    current_price = Decimal('0')
    if current_tier_config:
        if current_subscription_type == 'yearly' and current_tier_config.yearly_price:
            current_price = current_tier_config.yearly_price
        else:
            current_price = current_tier_config.monthly_price or Decimal('0')
    
    # 检查是否已经是该等级和订阅类型
    if subscription.tier == body.tier_name and current_subscription_type == body.subscription_type:
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message=f'您已经是 {target_tier.display_name} {"年度" if body.subscription_type == "yearly" else "月度"}用户',
        ))
    
    # 验证订阅类型
    if body.subscription_type not in ('monthly', 'yearly'):
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message='无效的订阅类型，请选择 monthly 或 yearly',
        ))
    
    # 年度订阅用户不能降级到月度
    if current_subscription_type == 'yearly' and body.subscription_type == 'monthly':
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message='年度订阅用户不能切换为月度订阅',
        ))
    
    # 检查是否降级
    target_price_monthly = target_tier.monthly_price or Decimal('0')
    current_price_monthly = current_tier_config.monthly_price if current_tier_config else Decimal('0')
    if target_price_monthly < current_price_monthly:
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message='不支持降级订阅',
        ))
    
    # 年度订阅需要配置年费价格
    if body.subscription_type == 'yearly' and not target_tier.yearly_price:
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message=f'{target_tier.display_name} 暂不支持年度订阅',
        ))
    
    # 计算价格
    if body.subscription_type == 'yearly':
        original_price = target_tier.yearly_price
    else:
        original_price = target_tier.monthly_price
    
    # 计算当前订阅剩余价值
    subscription_end = getattr(subscription, 'subscription_end_date', None)
    remaining_value, remaining_days = _calculate_remaining_value(
        current_price,
        subscription_end,
        current_subscription_type,
    )
    
    # 计算实际支付价格
    final_price = original_price - remaining_value
    if final_price < 0:
        final_price = Decimal('0')
    
    # 模拟支付 - 生成订单号
    order_id = f'SUB-{uuid.uuid4().hex[:12].upper()}'
    subscription_type_display = '年度' if body.subscription_type == 'yearly' else '月度'
    log.info(f'[Subscription] 模拟支付: user_id={user_id}, tier={body.tier_name}, type={body.subscription_type}, '
             f'order_id={order_id}, original_price={original_price}, remaining_value={remaining_value}, final_price={final_price}')
    
    # 获取当前总可用积分
    balance_before = await credit_service.get_total_available_credits(db, user_id, app_code)
    
    # 计算订阅时间
    now = timezone.now()
    if body.subscription_type == 'yearly':
        # 年度订阅：订阅期限一年，每月赠送积分
        subscription_end_new = now + timedelta(days=365)
        cycle_end = now + timedelta(days=30)  # 第一次积分有效期
        next_grant = now + timedelta(days=30)  # 下个月赠送
    else:
        # 月度订阅：订阅期限一个月
        subscription_end_new = now + timedelta(days=30)
        cycle_end = now + timedelta(days=30)
        next_grant = None
    
    # 更新用户订阅
    old_tier = subscription.tier
    subscription.tier = body.tier_name
    subscription.subscription_type = body.subscription_type
    subscription.monthly_credits = target_tier.monthly_credits
    subscription.billing_cycle_start = now
    subscription.billing_cycle_end = cycle_end
    subscription.subscription_start_date = now
    subscription.subscription_end_date = subscription_end_new
    subscription.next_grant_date = next_grant
    subscription.status = 'active'
    
    # 创建新的积分余额记录（第一次赠送的积分）
    from backend.app.user_tier.model import CreditTransaction, UserCreditBalance
    upgrade_balance = UserCreditBalance(
        app_code=app_code,
        user_id=user_id,
        credit_type='monthly',
        original_amount=target_tier.monthly_credits,
        used_amount=Decimal('0'),
        remaining_amount=target_tier.monthly_credits,
        expires_at=cycle_end,
        granted_at=now,
        source_type='subscription_upgrade',
        source_reference_id=order_id,
        description=f'{subscription_type_display}订阅: {body.tier_name} (第1个月)',
    )
    db.add(upgrade_balance)
    
    # 更新 subscription 汇总字段（累加新积分）
    new_total = balance_before + target_tier.monthly_credits
    subscription.current_credits = new_total
    
    # 记录交易
    transaction = CreditTransaction(
        app_code=app_code,
        user_id=user_id,
        transaction_type='subscription_upgrade',
        credits=target_tier.monthly_credits,
        balance_before=balance_before,
        balance_after=new_total,
        reference_id=order_id,
        reference_type='payment',
        description=f'{subscription_type_display}订阅: {old_tier} -> {body.tier_name}',
        extra_data={
            'old_tier': old_tier,
            'new_tier': body.tier_name,
            'subscription_type': body.subscription_type,
            'original_price': float(original_price),
            'remaining_value': float(remaining_value),
            'final_price': float(final_price),
        },
    )
    db.add(transaction)
    
    log.info(f'[Subscription] 订阅升级成功: user_id={user_id}, {old_tier} -> {body.tier_name} ({body.subscription_type})')
    
    price_info = f'（原价¥{original_price}'
    if remaining_value > 0:
        price_info += f'，折抵¥{remaining_value}'
    price_info += f'，实付¥{final_price}）'
    
    return response_base.success(data=PaymentResult(
        success=True,
        order_id=order_id,
        message=f'成功订阅 {target_tier.display_name} {subscription_type_display}版{price_info}',
        new_credits=subscription.current_credits,
        new_tier=body.tier_name,
    ))


@router.post(
    '/purchase',
    summary='购买积分包（模拟支付）',
    description='购买积分包，使用模拟支付',
    dependencies=[DependsJwtAuth],
)
async def purchase_credits(
    request: Request,
    db: CurrentSessionTransaction,
    body: PurchaseCreditsRequest,
) -> ResponseSchemaModel[PaymentResult]:
    """购买积分包"""
    user_id = request.user.id
    app_code = request.state.app_code

    # 获取积分包
    package = await credit_package_dao.select_model(db, pk=body.package_id)
    if not package or not package.enabled:
        return response_base.fail(data=PaymentResult(
            success=False,
            order_id='',
            message='积分包不存在或未启用',
        ))
    
    # 计算总积分
    total_credits = package.credits + package.bonus_credits
    
    # 模拟支付 - 生成订单号
    order_id = f'CRD-{uuid.uuid4().hex[:12].upper()}'
    log.info(f'[Subscription] 模拟支付: user_id={user_id}, package={package.package_name}, order_id={order_id}, price={package.price}')
    
    # 增加用户积分
    subscription = await credit_service.add_credits(
        db,
        user_id=user_id,
        credits=total_credits,
        transaction_type='purchase',
        reference_id=order_id,
        reference_type='payment',
        description=f'购买积分包: {package.package_name} ({package.credits}+{package.bonus_credits})',
        is_purchased=True,
        app_code=app_code,
    )
    
    log.info(f'[Subscription] 积分购买成功: user_id={user_id}, credits={total_credits}, balance={subscription.current_credits}')
    
    return response_base.success(data=PaymentResult(
        success=True,
        order_id=order_id,
        message=f'成功购买 {package.package_name}，获得 {total_credits} 积分',
        new_credits=subscription.current_credits,
    ))
