"""一次性回填：把存量 hasn_agents.*_md 里残留的模板占位符就地渲染成真实值。

背景：「建档即替换」上线前创建的 Agent，其 soul/agents/user/memory_md 仍存模板原文（含 {{}}）。
因为已改为「落库即替换」，serve 端不再替换，故存量行必须真渲染（仅 bump revision 不够）。
本脚本复用 register_hasn_agent 的 _render_profile_vars 就地渲染，并 +1 profile_revision，
让 runtime 下次激活/装技能触发的 provision 重拉已渲染 profile。

用法（先本地 PG 15432，生产 huanxing 库同样跑一次）：
    uv run python -m backend.scripts.backfill_render_agent_profiles --dry-run   # 只看不写
    uv run python -m backend.scripts.backfill_render_agent_profiles            # 真跑提交

零 fake：只渲染真实占位符；无 {{}} 的字段跳过；owner 缺失则昵称回退 owner_id（不编造）。
"""
from __future__ import annotations

import argparse
import asyncio

import sqlalchemy as sa

from backend.app.hasn.model import HasnAgents, HasnHumans
from backend.app.hasn.service.hasn_auth import _format_created_at, _render_profile_vars
from backend.database.db import async_db_session

_MD_FIELDS = ('soul_md', 'agents_md', 'user_md', 'memory_md')


async def _run(dry_run: bool) -> None:
    async with async_db_session() as db:
        rows = list(
            (
                await db.execute(
                    sa.select(HasnAgents).where(
                        sa.or_(*[getattr(HasnAgents, f).like('%{{%') for f in _MD_FIELDS])
                    )
                )
            )
            .scalars()
            .all()
        )
        print(f'candidates with placeholders: {len(rows)}')

        changed = 0
        for agent in rows:
            owner = (
                await db.execute(sa.select(HasnHumans).where(HasnHumans.hasn_id == agent.owner_id))
            ).scalar_one_or_none()
            owner_nickname = (getattr(owner, 'nickname', None) or agent.owner_id) if owner else agent.owner_id
            created_at = _format_created_at(getattr(agent, 'created_time', None))

            row_changed = False
            for field in _MD_FIELDS:
                cur = getattr(agent, field, None)
                if not cur or '{{' not in cur:
                    continue
                rendered = _render_profile_vars(
                    cur,
                    owner_nickname=owner_nickname,
                    owner_id=agent.owner_id,
                    display_name=agent.display_name,
                    agent_name=agent.agent_name,
                    star_id=agent.star_id,
                    agent_id=agent.hasn_id,
                    created_at=created_at,
                )
                if rendered != cur:
                    if not dry_run:
                        setattr(agent, field, rendered)
                    row_changed = True

            if row_changed:
                changed += 1
                if not dry_run and hasattr(agent, 'profile_revision'):
                    agent.profile_revision = (agent.profile_revision or 1) + 1
                print(f'  {"would render" if dry_run else "rendered"}: {agent.hasn_id} ({agent.star_id})')

        if not dry_run:
            await db.commit()
            print(f'committed: rendered {changed} agents (+1 profile_revision each)')
        else:
            print(f'(dry-run) would render {changed} agents; nothing committed')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='只统计不写库')
    args = parser.parse_args()
    asyncio.run(_run(args.dry_run))


if __name__ == '__main__':
    main()
