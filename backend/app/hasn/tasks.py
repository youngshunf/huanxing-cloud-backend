"""HASN workbench and knowledge background tasks."""

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
