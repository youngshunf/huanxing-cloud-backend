from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.model import HxCreatorContent, HxCreatorPublish, HxCreatorProject
from backend.utils.timezone import timezone


class HxCreatorAnalyticsService:
    @staticmethod
    async def overview(*, db: AsyncSession, user_id: int, days: int = 7) -> dict:
        """
        数据总览：内容总数、发布总数、总阅读/点赞/评论，近 N 天新增内容数

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param days: 统计天数
        :return: 聚合数据
        """
        since = timezone.now() - timedelta(days=days)

        # 内容总数
        total_contents_result = await db.execute(
            select(func.count(HxCreatorContent.id)).where(HxCreatorContent.user_id == user_id)
        )
        total_contents = total_contents_result.scalar() or 0

        # 近 N 天新增内容
        recent_contents_result = await db.execute(
            select(func.count(HxCreatorContent.id)).where(
                HxCreatorContent.user_id == user_id,
                HxCreatorContent.created_time >= since,
            )
        )
        recent_contents = recent_contents_result.scalar() or 0

        # 发布汇总
        publish_agg_result = await db.execute(
            select(
                func.count(HxCreatorPublish.id),
                func.coalesce(func.sum(HxCreatorPublish.views), 0),
                func.coalesce(func.sum(HxCreatorPublish.likes), 0),
                func.coalesce(func.sum(HxCreatorPublish.comments), 0),
                func.coalesce(func.sum(HxCreatorPublish.shares), 0),
                func.coalesce(func.sum(HxCreatorPublish.favorites), 0),
            ).where(HxCreatorPublish.user_id == user_id)
        )
        row = publish_agg_result.one()
        total_publishes = row[0] or 0
        total_views = int(row[1])
        total_likes = int(row[2])
        total_comments = int(row[3])
        total_shares = int(row[4])
        total_favorites = int(row[5])

        # 项目数
        project_count_result = await db.execute(
            select(func.count(HxCreatorProject.id)).where(HxCreatorProject.user_id == user_id)
        )
        project_count = project_count_result.scalar() or 0

        # 各状态内容数
        status_result = await db.execute(
            select(
                HxCreatorContent.status,
                func.count(HxCreatorContent.id),
            ).where(HxCreatorContent.user_id == user_id).group_by(HxCreatorContent.status)
        )
        status_distribution = {row[0]: row[1] for row in status_result.all()}

        return {
            'period_days': days,
            'project_count': project_count,
            'total_contents': total_contents,
            'recent_contents': recent_contents,
            'total_publishes': total_publishes,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'total_favorites': total_favorites,
            'total_engagement': total_likes + total_comments + total_shares + total_favorites,
            'status_distribution': status_distribution,
        }

    @staticmethod
    async def top_contents(
        *,
        db: AsyncSession,
        user_id: int,
        metric: str = 'views',
        limit: int = 10,
    ) -> list[dict]:
        """
        热门内容排行

        :param metric: 排序指标（views/likes/comments/shares/favorites）
        :param limit: 返回条数
        """
        metric_col_map = {
            'views': HxCreatorPublish.views,
            'likes': HxCreatorPublish.likes,
            'comments': HxCreatorPublish.comments,
            'shares': HxCreatorPublish.shares,
            'favorites': HxCreatorPublish.favorites,
        }
        order_col = metric_col_map.get(metric, HxCreatorPublish.views)

        stmt = (
            select(
                HxCreatorContent.id,
                HxCreatorContent.title,
                HxCreatorContent.status,
                func.coalesce(func.sum(HxCreatorPublish.views), 0).label('total_views'),
                func.coalesce(func.sum(HxCreatorPublish.likes), 0).label('total_likes'),
                func.coalesce(func.sum(HxCreatorPublish.comments), 0).label('total_comments'),
                func.coalesce(func.sum(HxCreatorPublish.shares), 0).label('total_shares'),
                func.coalesce(func.sum(HxCreatorPublish.favorites), 0).label('total_favorites'),
            )
            .join(HxCreatorPublish, HxCreatorContent.id == HxCreatorPublish.content_id, isouter=True)
            .where(HxCreatorContent.user_id == user_id)
            .group_by(HxCreatorContent.id)
            .order_by(func.coalesce(func.sum(order_col), 0).desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                'content_id': row[0],
                'title': row[1],
                'status': row[2],
                'total_views': int(row[3]),
                'total_likes': int(row[4]),
                'total_comments': int(row[5]),
                'total_shares': int(row[6]),
                'total_favorites': int(row[7]),
            }
            for row in rows
        ]


hx_creator_analytics_service: HxCreatorAnalyticsService = HxCreatorAnalyticsService()
