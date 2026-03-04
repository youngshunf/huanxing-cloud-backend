"""压缩统计 API - 管理后台"""

from datetime import date

from fastapi import APIRouter, Query

from backend.app.llm.service.compress_stats_service import compress_stats_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '/summary',
    summary='压缩用量汇总',
    dependencies=[DependsJwtAuth],
)
async def get_compress_summary(
    db: CurrentSession,
    start_date: date | None = Query(None, description='开始日期'),
    end_date: date | None = Query(None, description='结束日期'),
) -> ResponseSchemaModel:
    """
    获取压缩用量汇总（管理后台看板）

    返回：
    - total_compressions: 总压缩次数
    - cache_hits / cache_hit_rate: 缓存命中数 / 命中率
    - total_input_tokens / total_output_tokens: 摘要生成总 token
    - total_cost: 平台总成本 (USD)
    - avg_generation_ms: 平均摘要生成耗时
    - compression_ratio: 压缩后 token / 压缩前 token 比率
    - secondary_compressions: 二次压缩次数
    """
    data = await compress_stats_service.get_summary(
        db, start_date=start_date, end_date=end_date
    )
    return response_base.success(data=data)


@router.get(
    '/daily',
    summary='每日压缩统计',
    dependencies=[DependsJwtAuth],
)
async def get_compress_daily(
    db: CurrentSession,
    days: int = Query(30, ge=1, le=365, description='天数'),
) -> ResponseSchemaModel:
    """获取每日压缩统计（图表数据）"""
    data = await compress_stats_service.get_daily_stats(db, days=days)
    return response_base.success(data=data)


@router.get(
    '/top-users',
    summary='压缩成本 Top 用户',
    dependencies=[DependsJwtAuth],
)
async def get_compress_top_users(
    db: CurrentSession,
    start_date: date | None = Query(None, description='开始日期'),
    end_date: date | None = Query(None, description='结束日期'),
    limit: int = Query(20, ge=1, le=100, description='返回数量'),
) -> ResponseSchemaModel:
    """获取压缩成本最高的用户（成本分布分析）"""
    data = await compress_stats_service.get_top_users(
        db, start_date=start_date, end_date=end_date, limit=limit
    )
    return response_base.success(data=data)
