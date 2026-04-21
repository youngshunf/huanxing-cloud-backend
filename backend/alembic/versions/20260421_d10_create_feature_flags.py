"""D10 create feature_flags + feature_flag_assignments

Revision ID: 20260421_d10_feature_flags
Revises: 20260421_b10_push_audit
Create Date: 2026-04-21 16:30:00.000000

Creates 2 tables backing M1 内测灰度: `feature_flags` (registry) +
`feature_flag_assignments` (per-hasn_id whitelist).

Source: docs/架构设计/移动端/08-构建打包与发布详细设计.md §9.1。
M1 决策: 纯国内发行不走 Play Console 灰度 track; 灰度由后端 feature flag
实现, 客户端启动时 GET /api/v1/app/feature-flags/{hasn_id} 拉取生效列表。
"""
import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260421_d10_feature_flags'
down_revision = '20260421_b10_push_audit'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'feature_flags',
        sa.Column(
            'id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment='主键 ID',
        ),
        sa.Column(
            'key',
            sa.String(length=64),
            nullable=False,
            server_default='',
            comment='flag 唯一 key',
        ),
        sa.Column(
            'description',
            sa.Text(),
            nullable=True,
            comment='人工备注',
        ),
        sa.Column(
            'default_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment='无 assignment 时的缺省启用状态',
        ),
        sa.Column(
            'payload',
            postgresql.JSONB(),
            nullable=True,
            comment='可选配置 JSON (客户端读)',
        ),
        sa.Column(
            'created_time',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='创建时间',
        ),
        sa.Column(
            'updated_time',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='更新时间',
        ),
        comment='M1 内测灰度 feature flag 注册表 [D10]',
    )
    op.create_unique_constraint(
        'uq_feature_flags_key',
        'feature_flags',
        ['key'],
    )

    op.create_table(
        'feature_flag_assignments',
        sa.Column(
            'id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment='主键 ID',
        ),
        sa.Column(
            'flag_id',
            sa.BigInteger(),
            sa.ForeignKey('feature_flags.id', ondelete='CASCADE'),
            nullable=False,
            comment='关联 feature_flags.id',
        ),
        sa.Column(
            'hasn_id',
            sa.String(length=40),
            nullable=False,
            server_default='',
            comment='内测白名单 hasn_id',
        ),
        sa.Column(
            'enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
            comment='显式覆盖 default_enabled',
        ),
        sa.Column(
            'created_time',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='创建时间',
        ),
        sa.Column(
            'updated_time',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='更新时间',
        ),
        comment='M1 内测灰度白名单 (按 hasn_id 覆盖 default_enabled) [D10]',
    )
    op.create_unique_constraint(
        'uq_feature_flag_assignments_flag_hasn',
        'feature_flag_assignments',
        ['flag_id', 'hasn_id'],
    )
    op.create_index(
        'ix_feature_flag_assignments_hasn_id',
        'feature_flag_assignments',
        ['hasn_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        'ix_feature_flag_assignments_hasn_id',
        table_name='feature_flag_assignments',
    )
    op.drop_constraint(
        'uq_feature_flag_assignments_flag_hasn',
        'feature_flag_assignments',
        type_='unique',
    )
    op.drop_table('feature_flag_assignments')
    op.drop_constraint(
        'uq_feature_flags_key',
        'feature_flags',
        type_='unique',
    )
    op.drop_table('feature_flags')
