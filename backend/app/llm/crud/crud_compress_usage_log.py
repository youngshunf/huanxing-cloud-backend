"""压缩用量日志 CRUD"""

from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.llm.model.compress_usage_log import CompressUsageLog


class CRUDCompressUsageLog(CRUDPlus[CompressUsageLog]):
    """压缩用量日志数据库操作类"""

    async def create(self, db: AsyncSession, obj: dict) -> CompressUsageLog:
        new_obj = CompressUsageLog(**obj)
        db.add(new_obj)
        await db.commit()
        await db.refresh(new_obj)
        return new_obj

    async def get_summary(
        self,
        db: AsyncSession,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        """获取压缩用量汇总（平台成本面板）"""
        stmt = select(
            func.count(CompressUsageLog.id).label('total_compressions'),
            func.count(
                func.nullif(CompressUsageLog.cache_hit, False)
            ).label('cache_hits'),
            func.coalesce(func.sum(CompressUsageLog.input_tokens), 0).label('total_input_tokens'),
            func.coalesce(func.sum(CompressUsageLog.output_tokens), 0).label('total_output_tokens'),
            func.coalesce(func.sum(CompressUsageLog.total_cost), Decimal(0)).label('total_cost'),
            func.coalesce(func.avg(CompressUsageLog.generation_ms), 0).label('avg_generation_ms'),
            func.coalesce(func.sum(CompressUsageLog.original_tokens), 0).label('total_original_tokens'),
            func.coalesce(func.sum(CompressUsageLog.compressed_tokens), 0).label('total_compressed_tokens'),
            func.count(
                func.nullif(CompressUsageLog.secondary_compression, False)
            ).label('secondary_compressions'),
        )

        if start_date:
            stmt = stmt.where(CompressUsageLog.created_time >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            stmt = stmt.where(CompressUsageLog.created_time <= datetime.combine(end_date, datetime.max.time()))

        result = await db.execute(stmt)
        row = result.one()

        total = row.total_compressions or 0
        cache_hits = int(row.cache_hits or 0)
        total_original = int(row.total_original_tokens or 0)
        total_compressed = int(row.total_compressed_tokens or 0)

        return {
            'total_compressions': total,
            'cache_hits': cache_hits,
            'cache_hit_rate': round(cache_hits / total * 100, 1) if total > 0 else 0,
            'total_input_tokens': int(row.total_input_tokens or 0),
            'total_output_tokens': int(row.total_output_tokens or 0),
            'total_cost': float(row.total_cost or 0),
            'avg_generation_ms': int(row.avg_generation_ms or 0),
            'total_original_tokens': total_original,
            'total_compressed_tokens': total_compressed,
            'compression_ratio': round(total_compressed / total_original * 100, 1) if total_original > 0 else 0,
            'secondary_compressions': int(row.secondary_compressions or 0),
        }

    async def get_daily_stats(
        self,
        db: AsyncSession,
        *,
        days: int = 30,
    ) -> list[dict]:
        """获取每日压缩统计"""
        start_date = date.today() - timedelta(days=days - 1)
        stmt = select(
            func.date(CompressUsageLog.created_time).label('date'),
            func.count(CompressUsageLog.id).label('compressions'),
            func.coalesce(func.sum(CompressUsageLog.total_cost), Decimal(0)).label('cost'),
            func.coalesce(func.sum(CompressUsageLog.input_tokens + CompressUsageLog.output_tokens), 0).label('tokens'),
        ).where(
            CompressUsageLog.created_time >= datetime.combine(start_date, datetime.min.time()),
        ).group_by(
            func.date(CompressUsageLog.created_time)
        ).order_by(
            func.date(CompressUsageLog.created_time)
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                'date': str(row.date),
                'compressions': row.compressions,
                'cost': float(row.cost),
                'tokens': int(row.tokens),
            }
            for row in rows
        ]

    async def get_top_users(
        self,
        db: AsyncSession,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """获取压缩次数最多的用户（成本分布）"""
        stmt = select(
            CompressUsageLog.user_id,
            func.count(CompressUsageLog.id).label('compressions'),
            func.coalesce(func.sum(CompressUsageLog.total_cost), Decimal(0)).label('cost'),
            func.coalesce(func.sum(CompressUsageLog.input_tokens + CompressUsageLog.output_tokens), 0).label('tokens'),
        )

        if start_date:
            stmt = stmt.where(CompressUsageLog.created_time >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            stmt = stmt.where(CompressUsageLog.created_time <= datetime.combine(end_date, datetime.max.time()))

        stmt = stmt.group_by(CompressUsageLog.user_id).order_by(
            func.sum(CompressUsageLog.total_cost).desc()
        ).limit(limit)

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                'user_id': row.user_id,
                'compressions': row.compressions,
                'cost': float(row.cost),
                'tokens': int(row.tokens),
            }
            for row in rows
        ]


compress_usage_log_dao: CRUDCompressUsageLog = CRUDCompressUsageLog(CompressUsageLog)
