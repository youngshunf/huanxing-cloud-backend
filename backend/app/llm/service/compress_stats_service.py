"""压缩统计服务
@author Guardian

提供压缩用量统计和成本追踪能力。
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.llm.crud.crud_compress_usage_log import compress_usage_log_dao
from backend.common.log import log

# Sonnet 4.5 定价 (USD per 1K tokens)
SONNET_INPUT_COST_PER_1K = Decimal('0.003')
SONNET_OUTPUT_COST_PER_1K = Decimal('0.015')


class CompressStatsService:
    """压缩统计服务"""

    @staticmethod
    def calculate_cost(input_tokens: int, output_tokens: int) -> tuple[Decimal, Decimal, Decimal]:
        """
        计算摘要生成成本

        Returns:
            (input_cost, output_cost, total_cost)
        """
        input_cost = Decimal(input_tokens) / 1000 * SONNET_INPUT_COST_PER_1K
        output_cost = Decimal(output_tokens) / 1000 * SONNET_OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost
        return input_cost, output_cost, total_cost

    async def record_compression(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        api_key_id: int,
        request_id: str,
        summary_model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        original_messages: int = 0,
        compressed_messages: int = 0,
        original_tokens: int = 0,
        compressed_tokens: int = 0,
        summary_blocks: int = 0,
        cache_hit: bool = False,
        secondary_compression: bool = False,
        degraded_keep_count: int | None = None,
        generation_ms: int = 0,
        ip_address: str | None = None,
    ) -> None:
        """记录一次压缩用量"""
        input_cost, output_cost, total_cost = self.calculate_cost(input_tokens, output_tokens)

        try:
            await compress_usage_log_dao.create(db, {
                'user_id': user_id,
                'api_key_id': api_key_id,
                'request_id': request_id,
                'summary_model': summary_model,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': total_cost,
                'original_messages': original_messages,
                'compressed_messages': compressed_messages,
                'original_tokens': original_tokens,
                'compressed_tokens': compressed_tokens,
                'summary_blocks': summary_blocks,
                'cache_hit': cache_hit,
                'secondary_compression': secondary_compression,
                'degraded_keep_count': degraded_keep_count,
                'generation_ms': generation_ms,
                'ip_address': ip_address,
            })
        except Exception as e:
            log.warning(f'[智能压缩] 记录压缩用量失败，忽略: {e}')

    async def get_summary(
        self,
        db: AsyncSession,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        """获取压缩用量汇总"""
        return await compress_usage_log_dao.get_summary(db, start_date=start_date, end_date=end_date)

    async def get_daily_stats(
        self,
        db: AsyncSession,
        *,
        days: int = 30,
    ) -> list[dict]:
        """获取每日压缩统计"""
        return await compress_usage_log_dao.get_daily_stats(db, days=days)

    async def get_top_users(
        self,
        db: AsyncSession,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """获取压缩成本 Top 用户"""
        return await compress_usage_log_dao.get_top_users(
            db, start_date=start_date, end_date=end_date, limit=limit
        )


compress_stats_service = CompressStatsService()
