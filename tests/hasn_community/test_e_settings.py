"""
E-backend 回归：个人社区设置 + 黑名单 + Agent 广场筛选。
doc-13 §2.3/§3.3/§3.4。连真实 PG，事务回滚隔离。
"""
from __future__ import annotations

import pytest

from backend.app.hasn_community.service.community_service import community_service
from tests.hasn_community.conftest import seed_agent, seed_human, seed_post


@pytest.mark.asyncio
async def test_settings_defaults_and_patch(db):
    user = await seed_human(db, nickname='设置用户')

    # 默认值
    s0 = await community_service.get_community_settings(db, hasn_id=user['hasn_id'])
    assert s0['show_profile'] is True
    assert s0['default_comment_policy'] == 'all'
    assert s0['notify']['like'] is True

    # 部分 patch
    s1 = await community_service.update_community_settings(
        db, hasn_id=user['hasn_id'],
        patch={'searchable': False, 'notify': {'like': False}},
    )
    assert s1['searchable'] is False
    assert s1['notify']['like'] is False
    assert s1['notify']['comment'] is True  # 未改的保留默认
    assert s1['show_profile'] is True  # 未改的保留

    # 持久化
    s2 = await community_service.get_community_settings(db, hasn_id=user['hasn_id'])
    assert s2['searchable'] is False
    assert s2['notify']['like'] is False


@pytest.mark.asyncio
async def test_blocks_add_list_remove(db):
    user = await seed_human(db, nickname='本人')
    target = await seed_human(db, nickname='讨厌的人')

    await community_service.add_block(
        db, blocker_hasn_id=user['hasn_id'], blocked_hasn_id=target['hasn_id'], reason='spam'
    )
    blocks = await community_service.list_blocks(db, blocker_hasn_id=user['hasn_id'])
    assert len(blocks['items']) == 1
    assert blocks['items'][0]['blocked_hasn_id'] == target['hasn_id']
    assert blocks['items'][0]['reason'] == 'spam'

    # 幂等
    await community_service.add_block(
        db, blocker_hasn_id=user['hasn_id'], blocked_hasn_id=target['hasn_id']
    )
    blocks2 = await community_service.list_blocks(db, blocker_hasn_id=user['hasn_id'])
    assert len(blocks2['items']) == 1

    await community_service.remove_block(
        db, blocker_hasn_id=user['hasn_id'], blocked_hasn_id=target['hasn_id']
    )
    blocks3 = await community_service.list_blocks(db, blocker_hasn_id=user['hasn_id'])
    assert len(blocks3['items']) == 0


@pytest.mark.asyncio
async def test_cannot_block_self(db):
    user = await seed_human(db, nickname='本人')
    from backend.common.exception import errors

    with pytest.raises(errors.RequestError):
        await community_service.add_block(
            db, blocker_hasn_id=user['hasn_id'], blocked_hasn_id=user['hasn_id']
        )


@pytest.mark.asyncio
async def test_recommended_agents_capability_filter(db):
    owner = await seed_human(db, nickname='星主')
    await seed_agent(
        db, owner_hasn_id=owner['hasn_id'], display_name='代码分身',
        capability_summary_json={'skills': ['代码生成', 'Python']},
    )
    await seed_agent(
        db, owner_hasn_id=owner['hasn_id'], display_name='市场分身',
        capability_summary_json={'skills': ['市场营销']},
    )

    # 按能力过滤
    res = await community_service.get_recommended_agents(
        db, viewer_user_id=owner['user_id'], capability='代码生成', limit=10
    )
    names = {a['display_name'] for a in res['items']}
    assert '代码分身' in names
    assert '市场分身' not in names


@pytest.mark.asyncio
async def test_recommended_agents_sort_and_pagination(db):
    owner = await seed_human(db, nickname='星主')
    for i in range(3):
        await seed_agent(
            db, owner_hasn_id=owner['hasn_id'], display_name=f'分身{i}',
            capability_summary_json={'skills': ['通用']},
        )

    page1 = await community_service.get_recommended_agents(
        db, viewer_user_id=owner['user_id'], capability='通用', sort='relevance', limit=2
    )
    assert len(page1['items']) == 2
    assert page1['next_cursor'] is not None

    page2 = await community_service.get_recommended_agents(
        db, viewer_user_id=owner['user_id'], capability='通用', sort='relevance',
        limit=2, cursor=page1['next_cursor'],
    )
    ids1 = {a['hasn_id'] for a in page1['items']}
    ids2 = {a['hasn_id'] for a in page2['items']}
    assert ids1.isdisjoint(ids2)


@pytest.mark.asyncio
async def test_recommended_agents_excludes_social_disabled(db):
    owner = await seed_human(db, nickname='星主')
    # seed_agent 默认 social_enabled=true；直接插一个 social_enabled=false 验证排除
    from sqlalchemy import text

    from backend.database.db import uuid4_str
    hidden_id = f'a_{uuid4_str()[:20]}'
    await db.execute(
        text(
            "INSERT INTO hasn_agents (hasn_id, star_id, owner_id, agent_name, display_name, type, role, "
            "status, created_via, api_key_hash, avatar, bio, capability_summary_json, profile_json, "
            "social_enabled, created_time, updated_time) VALUES (:h, :s, :o, '隐藏', '隐藏分身', 'agent', "
            "'assistant', 'active', 'test', :k, '', '', '{}'::jsonb, '{}'::jsonb, false, now(), now())"
        ),
        {'h': hidden_id, 's': f's_{uuid4_str()[:12]}', 'o': owner['hasn_id'], 'k': uuid4_str().replace('-', '')[:64]},
    )
    await db.flush()

    res = await community_service.get_recommended_agents(db, viewer_user_id=owner['user_id'], limit=50)
    ids = {a['hasn_id'] for a in res['items']}
    assert hidden_id not in ids
