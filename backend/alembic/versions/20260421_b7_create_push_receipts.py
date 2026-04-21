"""B7 create push_receipts

Revision ID: 20260421_b7_push_receipts
Revises: 20260421_b3_push_tokens
Create Date: 2026-04-21 13:45:00.000000

Creates `push_receipts` table for M1 客户端推送到达回执 (到达率指标)。

Source: docs/架构设计/移动端/04-推送触达与后台运行模型详细设计.md §12.3。
"""
import sqlalchemy as sa

from alembic import op

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260421_b7_push_receipts'
down_revision = '20260421_b3_push_tokens'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'push_receipts',
        sa.Column(
            'id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment='主键 ID',
        ),
        sa.Column(
            'trace_id',
            sa.String(length=128),
            nullable=False,
            server_default='',
            comment='推送 trace (B6 生成, conv:{cid})',
        ),
        sa.Column(
            'hasn_id',
            sa.String(length=40),
            nullable=False,
            server_default='',
            comment='归属 owner 的 hasn_id',
        ),
        sa.Column(
            'channel',
            sa.String(length=16),
            nullable=False,
            server_default='umeng_push',
            comment="推送通道 (M1 固定 'umeng_push')",
        ),
        sa.Column(
            'received_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='客户端收到推送的绝对时间',
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
        comment='M1 移动端推送到达回执表 (到达率上报) [B7]',
    )
    op.create_index(
        'ix_push_receipts_trace_id',
        'push_receipts',
        ['trace_id'],
        unique=False,
    )
    op.create_index(
        'ix_push_receipts_hasn_id',
        'push_receipts',
        ['hasn_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_push_receipts_hasn_id', table_name='push_receipts')
    op.drop_index('ix_push_receipts_trace_id', table_name='push_receipts')
    op.drop_table('push_receipts')
