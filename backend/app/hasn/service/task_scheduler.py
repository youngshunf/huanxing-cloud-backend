"""HASN Task Scheduler（云端后台调度器）

每分钟 tick 一次，查询到期任务，通过 HASN 协议发送 TaskExec 消息到 Agent 所在的节点。

关键设计：
- at-most-once：预先推进 next_run_at，防止重复执行
- 预期最长执行时间 600s
- 链式任务：context_from_task_id 注入上次执行结果
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone as tz
from typing import Any, Dict, List, Optional
from croniter import croniter

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db import async_session_factory
from backend.app.hasn.model.hasn_task import HasnTask
from backend.app.hasn.model.hasn_task_run import HasnTaskRun
from backend.app.hasn.service.ws_router import ws_router

logger = logging.getLogger(__name__)

TICK_INTERVAL_SECONDS = 60
TASK_EXEC_TIMEOUT_SECONDS = 600


class TaskSchedulerService:
    """云端任务调度器"""

    def __init__(self) -> None:
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """启动调度器"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info('[TaskScheduler] started')

    async def stop(self) -> None:
        """停止调度器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info('[TaskScheduler] stopped')

    async def _run_loop(self) -> None:
        """主循环：每分钟 tick 一次"""
        while self._running:
            try:
                count = await self.tick()
                if count > 0:
                    logger.info(f'[TaskScheduler] tick dispatched {count} tasks')
            except Exception:
                logger.exception('[TaskScheduler] tick error')
            await asyncio.sleep(TICK_INTERVAL_SECONDS)

    async def tick(self) -> int:
        """
        调度器 tick：
        1. 查找 enabled=true AND next_run_at <= NOW() 的任务
        2. 预先推进 next_run_at（at-most-once）
        3. 创建 hasn_task_run 记录（status=pending）
        4. 发送 TaskExec 消息到 Agent 所在节点
        """
        now = datetime.now(tz.utc)
        dispatched = 0

        async with async_session_factory() as session:
            # 1. 查找到期任务
            stmt = (
                select(HasnTask)
                .where(HasnTask.enabled.is_(True))
                .where(HasnTask.next_run_at <= now)
                .limit(100)
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            for task in tasks:
                try:
                    await self._dispatch_task(session, task, now)
                    dispatched += 1
                except Exception:
                    logger.exception(f'[TaskScheduler] dispatch task {task.id} failed')

            await session.commit()

        return dispatched

    async def _dispatch_task(
        self,
        session: AsyncSession,
        task: HasnTask,
        now: datetime,
    ) -> None:
        """处理单个到期任务"""
        # 预先推进 next_run_at（at-most-once）
        next_run = self._calc_next_run(task, now)
        task.next_run_at = next_run
        task.last_run_at = now
        task.run_count = (task.run_count or 0) + 1
        task.repeat_completed = (task.repeat_completed or 0) + 1

        # 检查是否需要标记 completed
        if task.schedule_type == 'once':
            task.enabled = False
            task.state = 'completed'
        elif task.repeat_times is not None and task.repeat_completed >= task.repeat_times:
            task.enabled = False
            task.state = 'completed'

        # 2. 构建 prompt（含链式上下文）
        prompt = task.prompt
        context: Dict[str, Any] = {}
        if task.context_from_task_id:
            ctx = await self._load_context_from(session, task.context_from_task_id)
            if ctx:
                context['previous_output'] = ctx

        # 3. 创建 hasn_task_run（status=pending）
        task_run = HasnTaskRun(
            task_id=task.id,
            agent_id=task.agent_id,
            status='pending',
            prompt_snapshot=prompt,
            create_time=now,
        )
        session.add(task_run)
        await session.flush()  # 获取 task_run.id

        # 4. 发送 TaskExec 消息到 Agent
        task_exec_msg = {
            'type': 'task_exec',
            'task_id': task.id,
            'run_id': task_run.id,
            'agent_id': task.agent_id,
            'prompt': prompt,
            'skill_bundles': task.skill_bundle_ids or [],
            'skills': task.skill_ids or [],
            'enabled_toolsets': task.enabled_toolsets,
            'context': context,
        }

        pushed = await ws_router.push_message_to(task.agent_id, task_exec_msg)
        if not pushed:
            logger.warning(
                f'[TaskScheduler] task {task.id} agent {task.agent_id} offline, '
                f'message queued'
            )

    def _calc_next_run(self, task: HasnTask, now: datetime) -> Optional[datetime]:
        """根据 schedule_type 计算下一次执行时间"""
        config = task.schedule_config or {}

        if task.schedule_type == 'once':
            return None

        if task.schedule_type == 'interval':
            minutes = config.get('minutes', 60)
            return now + timedelta(minutes=minutes)

        if task.schedule_type == 'cron':
            expr = config.get('expr', '0 * * * *')
            try:
                cron = croniter(expr, now)
                return cron.get_next(datetime)
            except Exception:
                logger.error(f'[TaskScheduler] invalid cron expr: {expr}')
                return now + timedelta(hours=1)

        return None

    async def _load_context_from(
        self, session: AsyncSession, task_id: int
    ) -> Optional[str]:
        """加载链式任务的上下文（上一次执行结果）"""
        stmt = (
            select(HasnTaskRun)
            .where(HasnTaskRun.task_id == task_id)
            .where(HasnTaskRun.status == 'success')
            .order_by(HasnTaskRun.create_time.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        run = result.scalar_one_or_none()
        return run.output if run else None

    async def handle_task_result(
        self,
        run_id: int,
        status: str,
        output: Optional[str] = None,
        error: Optional[str] = None,
        model: Optional[str] = None,
        token_usage: Optional[Dict[str, int]] = None,
        duration_ms: Optional[int] = None,
    ) -> bool:
        """处理 hasn-node 回传的 TaskResult"""
        async with async_session_factory() as session:
            stmt = select(HasnTaskRun).where(HasnTaskRun.id == run_id)
            result = await session.execute(stmt)
            task_run = result.scalar_one_or_none()

            if not task_run:
                logger.warning(f'[TaskScheduler] task_run {run_id} not found')
                return False

            task_run.status = status
            task_run.output = output
            task_run.error = error
            task_run.model = model
            task_run.token_usage = token_usage
            task_run.duration_ms = duration_ms
            task_run.finished_at = datetime.now(tz.utc)

            # 更新 hasn_task 的 last_status/last_error
            task_stmt = select(HasnTask).where(HasnTask.id == task_run.task_id)
            task_result = await session.execute(task_stmt)
            task = task_result.scalar_one_or_none()
            if task:
                task.last_status = status
                task.last_error = error

            await session.commit()
            return True


task_scheduler = TaskSchedulerService()
