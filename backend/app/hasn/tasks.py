"""HASN workbench and knowledge background tasks."""

from datetime import datetime, timedelta

from backend.app.hasn.service.ragflow_subscriber import SqlAlchemyRAGFlowActions
from backend.app.task.celery import celery_app


@celery_app.task(name='hasn_ragflow_compensate_pending_credentials', bind=True, max_retries=5)
async def hasn_ragflow_compensate_pending_credentials(self) -> str:
    """Backfill pending RAGFlow credentials for approved enterprise members."""
    actions = SqlAlchemyRAGFlowActions()
    try:
        created = await actions.compensate_pending_credentials()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc
    return f'created={created}'


@celery_app.task(name='hasn_check_agent_heartbeat_timeout', bind=True)
async def hasn_check_agent_heartbeat_timeout(self) -> str:
    """检查 agent 心跳超时，将超过 1 小时未上报的 agent 标记为离线。

    定时执行：每 5 分钟一次
    超时阈值：1 小时
    """
    import sqlalchemy as sa
    from backend.app.hasn.model import HasnAgents
    from backend.database.db import async_db_session

    timeout_threshold = datetime.utcnow() - timedelta(hours=1)

    async with async_db_session() as session:
        # 查找超时的 agent：在线状态为 online 且最后心跳时间超过 1 小时
        result = await session.execute(
            sa.update(HasnAgents)
            .where(
                HasnAgents.online_status == 'online',
                HasnAgents.last_heartbeat_at < timeout_threshold,
            )
            .values(
                online_status='offline',
                binding_status='unbound',
                binding_node_id=None,
            )
        )
        await session.commit()

        count = result.rowcount
        if count > 0:
            return f'marked {count} agents as offline due to heartbeat timeout'
        return 'no agents timed out'
