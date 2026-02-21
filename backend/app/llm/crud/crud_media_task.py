"""媒体任务 CRUD"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.llm.model.media_task import MediaTask


class CRUDMediaTask(CRUDPlus[MediaTask]):
    """媒体任务数据库操作类"""

    async def get(self, db: AsyncSession, pk: int) -> MediaTask | None:
        return await self.select_model(db, pk)

    async def get_by_task_id(self, db: AsyncSession, task_id: str) -> MediaTask | None:
        """按任务 ID 查询"""
        return await self.select_model_by_column(db, task_id=task_id)

    async def get_by_vendor_task_id(self, db: AsyncSession, vendor_task_id: str) -> MediaTask | None:
        """按厂商任务 ID 查询"""
        return await self.select_model_by_column(db, vendor_task_id=vendor_task_id)

    async def get_pending_tasks(self, db: AsyncSession) -> list[MediaTask]:
        """获取待轮询的任务"""
        stmt = select(MediaTask).where(
            MediaTask.status == 'processing',
            MediaTask.vendor_task_id.isnot(None),
        ).order_by(MediaTask.created_time.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_list(
        self,
        *,
        user_id: int | None = None,
        media_type: str | None = None,
        status: str | None = None,
    ) -> Select:
        """获取任务列表"""
        filters = {}
        if user_id is not None:
            filters['user_id'] = user_id
        if media_type is not None:
            filters['media_type'] = media_type
        if status is not None:
            filters['status'] = status
        return await self.select_order('created_time', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: MediaTask) -> MediaTask:
        """创建任务"""
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update_status(
        self,
        db: AsyncSession,
        task_id: str,
        *,
        status: str,
        progress: int | None = None,
        vendor_task_id: str | None = None,
        vendor_urls: list | None = None,
        oss_urls: list | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        credits_cost: Decimal | None = None,
        completed_at: datetime | None = None,
        poll_count: int | None = None,
    ) -> MediaTask | None:
        """更新任务状态"""
        task = await self.get_by_task_id(db, task_id)
        if not task:
            return None
        task.status = status
        if progress is not None:
            task.progress = progress
        if vendor_task_id is not None:
            task.vendor_task_id = vendor_task_id
        if vendor_urls is not None:
            task.vendor_urls = vendor_urls
        if oss_urls is not None:
            task.oss_urls = oss_urls
        if error_code is not None:
            task.error_code = error_code
        if error_message is not None:
            task.error_message = error_message
        if credits_cost is not None:
            task.credits_cost = credits_cost
        if completed_at is not None:
            task.completed_at = completed_at
        if poll_count is not None:
            task.poll_count = poll_count
        await db.flush()
        return task


media_task_dao: CRUDMediaTask = CRUDMediaTask(MediaTask)
