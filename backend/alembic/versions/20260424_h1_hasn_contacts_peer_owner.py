"""H1 drop-recreate hasn_contacts with peer_owner_id + tags text[]

Revision ID: 20260424_h1_contacts_owner
Revises: 20260421_d10_feature_flags
Create Date: 2026-04-24 21:20:00.000000

Drop-recreates `hasn_contacts` to align with the HASN Contacts Unification
milestone (Phase 1 US-001). User confirmed the table currently carries no
production data, so a hard drop-recreate is safe. Adds `peer_owner_id`
(nullable; distinguishes "our agent" vs. "someone else's agent") and fixes
`tags` to `text[]` (ORM/schema now typed as `list[str]`).

Source: tasks/prd-hasn-contacts-unification.md §3 US-001.
"""
import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260424_h1_contacts_owner'
down_revision = '20260421_d10_feature_flags'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop legacy indexes + table if present (empty in all environments per
    # HASN Contacts Unification PRD).
    op.execute('DROP INDEX IF EXISTS idx_contact_owner')
    op.execute('DROP INDEX IF EXISTS idx_contact_peer')
    op.execute('DROP INDEX IF EXISTS idx_contact_type')
    op.execute('DROP INDEX IF EXISTS idx_contact_level')
    op.execute('DROP INDEX IF EXISTS idx_contact_status')
    op.execute('DROP INDEX IF EXISTS idx_contact_expire')
    op.execute('DROP INDEX IF EXISTS idx_contact_subscription')
    op.execute('DROP INDEX IF EXISTS idx_contact_peer_owner')
    op.execute('DROP TABLE IF EXISTS hasn_contacts CASCADE')

    op.create_table(
        'hasn_contacts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('owner_id', sa.String(length=36), nullable=False, comment='关系拥有者 hasn_id'),
        sa.Column('peer_id', sa.String(length=36), nullable=False, comment='对方 hasn_id'),
        sa.Column(
            'peer_owner_id',
            sa.String(length=36),
            nullable=True,
            comment='对方归属人 hasn_id (peer 自己的 owner)',
        ),
        sa.Column('peer_type', sa.String(length=10), nullable=False, comment='对方类型 (human/agent)'),
        sa.Column(
            'relation_type',
            sa.String(length=20),
            nullable=False,
            server_default='social',
            comment='关系类型 (social/commerce/service/professional/platform)',
        ),
        sa.Column('trust_level', sa.SmallInteger(), nullable=False, server_default='1', comment='信任等级 0-5'),
        sa.Column('scope', postgresql.JSONB(), nullable=True, comment='关系作用域 (JSONB)'),
        sa.Column(
            'custom_permissions',
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment='自定义权限覆盖 (JSONB)',
        ),
        sa.Column('nickname', sa.String(length=100), nullable=True, comment='备注名'),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True, comment='分组标签 (text[])'),
        sa.Column('subscription', sa.Boolean(), nullable=False, server_default=sa.false(), comment='是否订阅推送'),
        sa.Column(
            'status',
            sa.String(length=20),
            nullable=False,
            server_default='pending',
            comment='状态 (pending/connected/blocked/archived)',
        ),
        sa.Column('request_message', sa.Text(), nullable=True, comment='好友请求附言'),
        sa.Column('auto_expire', sa.DateTime(timezone=True), nullable=True, comment='自动过期时间'),
        sa.Column('connected_at', sa.DateTime(timezone=True), nullable=True, comment='建立连接时间'),
        sa.Column('last_interaction_at', sa.DateTime(timezone=True), nullable=True, comment='最后互动时间'),
        sa.Column('interaction_count', sa.Integer(), nullable=False, server_default='0', comment='互动次数'),
        sa.Column(
            'created_time',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='创建时间',
        ),
        sa.Column('updated_time', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.UniqueConstraint('owner_id', 'peer_id', 'relation_type', name='uq_hasn_contact_relation'),
        comment='HASN 联系人关系表',
    )
    op.create_index('idx_contact_owner', 'hasn_contacts', ['owner_id'], unique=False)
    op.create_index('idx_contact_peer', 'hasn_contacts', ['peer_id'], unique=False)
    op.create_index('idx_contact_type', 'hasn_contacts', ['owner_id', 'relation_type'], unique=False)
    op.create_index(
        'idx_contact_level',
        'hasn_contacts',
        ['owner_id', 'relation_type', 'trust_level'],
        unique=False,
    )
    op.create_index('idx_contact_status', 'hasn_contacts', ['status'], unique=False)
    op.create_index(
        'idx_contact_expire',
        'hasn_contacts',
        ['auto_expire'],
        unique=False,
        postgresql_where=sa.text('auto_expire IS NOT NULL'),
    )
    op.create_index(
        'idx_contact_subscription',
        'hasn_contacts',
        ['owner_id'],
        unique=False,
        postgresql_where=sa.text('subscription = true'),
    )
    op.create_index(
        'idx_contact_peer_owner',
        'hasn_contacts',
        ['peer_owner_id'],
        unique=False,
        postgresql_where=sa.text('peer_owner_id IS NOT NULL'),
    )


def downgrade() -> None:
    op.drop_index('idx_contact_peer_owner', table_name='hasn_contacts')
    op.drop_index('idx_contact_subscription', table_name='hasn_contacts')
    op.drop_index('idx_contact_expire', table_name='hasn_contacts')
    op.drop_index('idx_contact_status', table_name='hasn_contacts')
    op.drop_index('idx_contact_level', table_name='hasn_contacts')
    op.drop_index('idx_contact_type', table_name='hasn_contacts')
    op.drop_index('idx_contact_peer', table_name='hasn_contacts')
    op.drop_index('idx_contact_owner', table_name='hasn_contacts')
    op.drop_table('hasn_contacts')
