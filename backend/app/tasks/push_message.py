"""B6 — 消息落库后触发友盟 U-Push + 1 秒窗口合并.

依据 docs/架构设计/移动端/04-推送触达与后台运行模型详细设计.md §8.3 / §8.6:

- HASN 消息持久化后由上游调 `push_message.delay(message_id)` 入 Celery 队列
- 同一 `conversation_id` 在 1 秒内的多条消息只下发一次推送 — 避免高频对话刷屏
- 合并键: Redis `hasn_push_dedup:{conv_id}`, SET NX EX=1 (首条 set 成功下发, 其余
  set 返回 None → 跳过下发)
- 推送 payload 不带消息正文 (不变式 §4) — 只带 title/body 占位 + trace_id

设计拆分 (方便测试):
- `_dispatch_for_message(db, message_id)` 业务函数 — 接收已开启事务的 AsyncSession;
  单元测试可直接 monkeypatch `hasn_messages_dao.get` / `redis_client.set` /
  `push_dispatcher.dispatch` 而无需启动 Celery.
- `_push_message_impl(message_id)` 顶层协程 — 负责打开 async_db_session,
  被 celery task wrapper 调用.
- `push_message` — `@celery_app.task` 装饰器, bind=True, Celery 自身 retry 控制.

失败策略:
- 消息不存在 (已硬删除 / message_id 错误) → 返回 'not-found', 不重试
- 下发失败 (PushDispatchError) → 日志 + 返回 'dispatch-error', 不自动重试
  (dispatcher 内部已做 3 次网络重试; 再 retry 会重复下发)
"""
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from backend.app.hasn.crud.crud_hasn_messages import hasn_messages_dao
from backend.app.services.push_dispatcher import PushDispatchError, dispatch
from backend.app.task.celery import celery_app
from backend.database.db import async_db_session
from backend.database.redis import redis_client

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

DEDUP_KEY_PREFIX = 'hasn_push_dedup:'
DEDUP_TTL_SECONDS = 1

# 推送占位文案 — 不变式 §4: 不下发消息正文. 客户端收到推送后主动拉取消息列表.
DEFAULT_PUSH_TITLE = '新消息'
DEFAULT_PUSH_BODY = '您有一条新消息'


def _build_dedup_key(conversation_id: str) -> str:
    return f'{DEDUP_KEY_PREFIX}{conversation_id}'


def _build_trace_id(conversation_id: str) -> str:
    """稳定 trace_id (同一 dedup 窗口内重放保持一致)."""
    return f'conv:{conversation_id}'


async def _dispatch_for_message(db: AsyncSession, message_id: int) -> str:
    """核心下发逻辑 (可被测试直接调用).

    返回短字符串标识结果: 'not-found' / 'dedup-skip' / 'no-token' /
    'dispatch-error' / 'sent:<n>'.
    """
    message = await hasn_messages_dao.get(db, message_id)
    if message is None:
        logger.info('[push_message] message_id=%s 不存在, 跳过', message_id)
        return 'not-found'

    conversation_id = str(message.conversation_id)
    to_id = message.to_id

    dedup_key = _build_dedup_key(conversation_id)
    # SET NX EX: 返回 True 表示首次设置成功 (下发); 返回 None 表示已存在 (跳过)
    acquired = await redis_client.set(
        dedup_key, '1', nx=True, ex=DEDUP_TTL_SECONDS,
    )
    if not acquired:
        logger.info(
            '[push_message] conv=%s 1s 窗口内已下发过, 合并跳过 (message_id=%s)',
            conversation_id, message_id,
        )
        return 'dedup-skip'

    payload = {
        'title': DEFAULT_PUSH_TITLE,
        'body': DEFAULT_PUSH_BODY,
        'trace_id': _build_trace_id(conversation_id),
    }

    try:
        result = await dispatch(db, hasn_id=to_id, payload=payload)
    except PushDispatchError:
        logger.exception(
            '[push_message] dispatch 失败: hasn_id=%s conv=%s',
            to_id, conversation_id,
        )
        return 'dispatch-error'

    if result.sent == 0:
        logger.info(
            '[push_message] hasn_id=%s 无 token, conv=%s (message_id=%s)',
            to_id, conversation_id, message_id,
        )
        return 'no-token'

    logger.info(
        '[push_message] 下发成功: conv=%s hasn_id=%s sent=%d task_id=%s',
        conversation_id, to_id, result.sent, result.task_id,
    )
    return f'sent:{result.sent}'


async def _push_message_impl(message_id: int) -> str:
    """打开 DB session 并委派给 `_dispatch_for_message`."""
    async with async_db_session() as db:
        return await _dispatch_for_message(db, message_id)


@celery_app.task(name='push_message', bind=True)
async def push_message(self, message_id: int) -> str:  # noqa: ANN001
    """Celery 任务入口 — `push_message.delay(message_id)` 触发.

    `self` 由 `bind=True` 提供, 暂不使用 (未来做 retry / trace 可扩展).
    """
    return await _push_message_impl(message_id)
