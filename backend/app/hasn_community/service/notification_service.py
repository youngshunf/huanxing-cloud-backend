"""
社区通知服务（doc-13 §2.1 / §3.1）。

- 复用共享表 hasn_notifications（target_id = 接收方 hasn_id，data = 结构化负载）。
- 触发模型：互动写库成功后，按 §2.1.3 矩阵写通知；Agent 内容/被关注额外 relay 给主人。
- 去重抑制：自己互动自己的内容不写通知。
- 读时聚合：列表按 (type, target_id) 在时间窗内折叠（aggregated 标记）。
- 通知本体不重新 codegen（表已存在），仅在此服务内组装/读写。
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.model import HasnAgents, HasnHumans
from backend.app.hasn.model.hasn_notifications import HasnNotifications
from backend.common.exception import errors

# type → 标题模板后缀（按内容类型）
_CONTENT_NOUN = {'post': '帖子', 'article': '文章', 'comment': '评论'}


class NotificationService:
    """社区通知服务"""

    @staticmethod
    async def _resolve_actor(db: AsyncSession, hasn_id: str) -> dict[str, Any]:
        """解析触发者展示信息（human/agent）。"""
        human = (
            await db.execute(select(HasnHumans).where(HasnHumans.hasn_id == hasn_id))
        ).scalar_one_or_none()
        if human:
            return {
                'hasn_id': hasn_id,
                'type': 'human',
                'display_name': human.nickname or hasn_id,
                'avatar': human.avatar or '',
            }
        agent = (
            await db.execute(select(HasnAgents).where(HasnAgents.hasn_id == hasn_id))
        ).scalar_one_or_none()
        if agent:
            return {
                'hasn_id': hasn_id,
                'type': 'agent',
                'display_name': agent.display_name or hasn_id,
                'avatar': agent.avatar or '',
            }
        return {'hasn_id': hasn_id, 'type': 'unknown', 'display_name': hasn_id, 'avatar': ''}

    @staticmethod
    async def _insert(
        db: AsyncSession,
        *,
        recipient_hasn_id: str,
        ntype: str,
        title: str,
        data: dict[str, Any],
    ) -> None:
        """插入一条未读通知。"""
        db.add(
            HasnNotifications(
                target_id=recipient_hasn_id,
                type=ntype,
                title=title,
                body=None,
                data=data,
                read=False,
            )
        )
        await db.flush()

    @staticmethod
    def _content_link(content_type: str, content_id: str) -> str:
        if content_type == 'article':
            return f'/community/articles/{content_id}'
        return f'/community/posts/{content_id}'

    @classmethod
    async def notify_content_interaction(
        cls,
        db: AsyncSession,
        *,
        ntype: str,
        actor_hasn_id: str,
        content_type: str,
        content_id: str,
        author_hasn_id: str,
        author_type: str,
        owner_hasn_id: str | None,
        preview: str | None = None,
        extra_recipient_hasn_id: str | None = None,
    ) -> None:
        """点赞/评论/收藏：通知内容作者；Agent 内容 relay 给主人；可选额外接收方（被回复者）。"""
        actor = await cls._resolve_actor(db, actor_hasn_id)
        noun = _CONTENT_NOUN.get(content_type, '内容')
        verb = {
            'community_like': '赞了你的',
            'community_comment': '评论了你的',
            'community_collect': '收藏了你的',
        }.get(ntype, '互动了你的')
        link = cls._content_link(content_type, content_id)
        base_data = {
            'actor': actor,
            'target': {'type': content_type, 'id': content_id},
            'preview': (preview or '')[:80],
            'link': link,
        }

        # 1) 通知内容作者（自己互动自己跳过）
        if author_hasn_id and author_hasn_id != actor_hasn_id:
            await cls._insert(
                db,
                recipient_hasn_id=author_hasn_id,
                ntype=ntype,
                title=f'{actor["display_name"]}{verb}{noun}',
                data=dict(base_data),
            )
            # 2) Agent 内容 relay 给主人
            if author_type == 'agent' and owner_hasn_id and owner_hasn_id not in (actor_hasn_id, author_hasn_id):
                relay_data = dict(base_data)
                relay_data['relay_from'] = author_hasn_id
                await cls._insert(
                    db,
                    recipient_hasn_id=owner_hasn_id,
                    ntype=ntype,
                    title=f'{actor["display_name"]}{verb}你的分身的{noun}',
                    data=relay_data,
                )

        # 3) 额外接收方（评论回复 → 父评论作者）
        if extra_recipient_hasn_id and extra_recipient_hasn_id not in (actor_hasn_id, author_hasn_id):
            reply_data = dict(base_data)
            await cls._insert(
                db,
                recipient_hasn_id=extra_recipient_hasn_id,
                ntype=ntype,
                title=f'{actor["display_name"]}回复了你的评论',
                data=reply_data,
            )

    @classmethod
    async def notify_follow(
        cls,
        db: AsyncSession,
        *,
        actor_hasn_id: str,
        target_hasn_id: str,
        target_type: str,
        target_owner_hasn_id: str | None = None,
    ) -> None:
        """被关注：通知被关注者；Agent 被关注 relay 给主人。"""
        if target_hasn_id == actor_hasn_id:
            return
        actor = await cls._resolve_actor(db, actor_hasn_id)
        data = {
            'actor': actor,
            'target': {'type': target_type, 'id': target_hasn_id},
            'link': f'/community/profiles/{actor_hasn_id}',
        }
        await cls._insert(
            db,
            recipient_hasn_id=target_hasn_id,
            ntype='community_follow',
            title=f'{actor["display_name"]}关注了你',
            data=dict(data),
        )
        if target_type == 'agent' and target_owner_hasn_id and target_owner_hasn_id not in (actor_hasn_id, target_hasn_id):
            relay = dict(data)
            relay['relay_from'] = target_hasn_id
            await cls._insert(
                db,
                recipient_hasn_id=target_owner_hasn_id,
                ntype='community_follow',
                title=f'{actor["display_name"]}关注了你的分身',
                data=relay,
            )

    @classmethod
    async def notify_draft_pending(
        cls,
        db: AsyncSession,
        *,
        owner_hasn_id: str,
        agent_hasn_id: str,
        content_type: str,
        content_id: str,
        preview: str | None = None,
    ) -> None:
        """Agent 草稿待确认：通知主人。"""
        if not owner_hasn_id:
            return
        actor = await cls._resolve_actor(db, agent_hasn_id)
        noun = _CONTENT_NOUN.get(content_type, '内容')
        await cls._insert(
            db,
            recipient_hasn_id=owner_hasn_id,
            ntype='community_draft_pending',
            title=f'你的分身 {actor["display_name"]} 有一篇{noun}待确认',
            data={
                'actor': actor,
                'target': {'type': content_type, 'id': content_id},
                'preview': (preview or '')[:80],
                'link': '/community/drafts',
                'relay_from': agent_hasn_id,
            },
        )

    # ==================== 读取 / 已读 ====================

    @staticmethod
    async def list_notifications(
        db: AsyncSession,
        *,
        recipient_hasn_id: str,
        types: list[str] | None = None,
        unread_only: bool = False,
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """通知列表（type/unread 过滤 + 游标分页 + 读时聚合）。"""
        stmt = select(HasnNotifications).where(HasnNotifications.target_id == recipient_hasn_id)
        if types:
            stmt = stmt.where(HasnNotifications.type.in_(types))
        if unread_only:
            stmt = stmt.where(HasnNotifications.read.is_(False))
        if cursor:
            stmt = stmt.where(HasnNotifications.id < int(cursor))
        stmt = stmt.order_by(HasnNotifications.id.desc()).limit(limit + 1)

        rows = (await db.execute(stmt)).scalars().all()
        has_more = len(rows) > limit
        rows = rows[:limit]

        # 读时聚合：同 (type, target_id) 折叠，标记 aggregated_count
        seen: dict[tuple, dict[str, Any]] = {}
        items: list[dict[str, Any]] = []
        for n in rows:
            data = n.data or {}
            target = data.get('target', {})
            key = (n.type, target.get('id'))
            if key in seen and key[1] is not None:
                seen[key]['aggregated_count'] += 1
                continue
            entry = {
                'id': n.id,
                'type': n.type,
                'title': n.title,
                'actor': data.get('actor'),
                'target': target,
                'preview': data.get('preview'),
                'link': data.get('link'),
                'relay_from': data.get('relay_from'),
                'read': n.read,
                'aggregated_count': 1,
                'created_time': n.created_time.isoformat() if n.created_time else None,
            }
            items.append(entry)
            if key[1] is not None:
                seen[key] = entry

        return {
            'items': items,
            'next_cursor': str(rows[-1].id) if has_more and rows else None,
            'aggregated': True,
        }

    @staticmethod
    async def unread_count(
        db: AsyncSession,
        *,
        recipient_hasn_id: str,
    ) -> dict[str, Any]:
        """未读总数 + 按 type 分组。"""
        total = (
            await db.execute(
                select(func.count())
                .select_from(HasnNotifications)
                .where(
                    HasnNotifications.target_id == recipient_hasn_id,
                    HasnNotifications.read.is_(False),
                )
            )
        ).scalar() or 0
        by_type_rows = (
            await db.execute(
                select(HasnNotifications.type, func.count())
                .where(
                    HasnNotifications.target_id == recipient_hasn_id,
                    HasnNotifications.read.is_(False),
                )
                .group_by(HasnNotifications.type)
            )
        ).all()
        return {
            'total': int(total),
            'by_type': {row[0]: int(row[1]) for row in by_type_rows},
        }

    @staticmethod
    async def mark_read(
        db: AsyncSession,
        *,
        recipient_hasn_id: str,
        notification_id: int,
    ) -> None:
        """标记单条已读（仅本人）。"""
        n = (
            await db.execute(
                select(HasnNotifications).where(
                    HasnNotifications.id == notification_id,
                    HasnNotifications.target_id == recipient_hasn_id,
                )
            )
        ).scalar_one_or_none()
        if not n:
            raise errors.NotFoundError(msg='通知不存在')
        n.read = True
        await db.flush()

    @staticmethod
    async def mark_all_read(
        db: AsyncSession,
        *,
        recipient_hasn_id: str,
        types: list[str] | None = None,
    ) -> int:
        """全部已读（可按 type 过滤），返回影响条数。"""
        stmt = select(HasnNotifications).where(
            HasnNotifications.target_id == recipient_hasn_id,
            HasnNotifications.read.is_(False),
        )
        if types:
            stmt = stmt.where(HasnNotifications.type.in_(types))
        rows = (await db.execute(stmt)).scalars().all()
        for n in rows:
            n.read = True
        await db.flush()
        return len(rows)


notification_service = NotificationService()
