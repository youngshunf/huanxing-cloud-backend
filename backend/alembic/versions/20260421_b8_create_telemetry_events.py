"""B8 create telemetry_events

Revision ID: 20260421_b8_telemetry_events
Revises: 20260421_b7_push_receipts
Create Date: 2026-04-21 14:00:00.000000

Creates `telemetry_events` table for M1 移动端业务埋点批量上报 (B8).

Source: docs/架构设计/移动端/10-观测崩溃与日志详细设计.md §6.1 + §14.4。
"""
import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260421_b8_telemetry_events'
down_revision = '20260421_b7_push_receipts'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'telemetry_events',
        sa.Column(
            'id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment='主键 ID',
        ),
        sa.Column(
            'hasn_id',
            sa.String(length=40),
            nullable=False,
            server_default='',
            comment='归属 owner 的 hasn_id',
        ),
        sa.Column(
            'event_type',
            sa.String(length=64),
            nullable=False,
            server_default='',
            comment='事件类型 (§6.1 枚举)',
        ),
        sa.Column(
            'properties',
            postgresql.JSONB(),
            nullable=True,
            comment='事件属性 JSON (客户端脱敏, 不含 PII/凭据/正文)',
        ),
        sa.Column(
            'occurred_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='客户端触发事件的绝对时间',
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
        comment='M1 移动端业务埋点表 (友盟 U-App 并行双写, §6.1) [B8]',
    )
    op.create_index(
        'ix_telemetry_events_hasn_id',
        'telemetry_events',
        ['hasn_id'],
        unique=False,
    )
    op.create_index(
        'ix_telemetry_events_event_type',
        'telemetry_events',
        ['event_type'],
        unique=False,
    )
    op.create_index(
        'ix_telemetry_events_occurred_at',
        'telemetry_events',
        ['occurred_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        'ix_telemetry_events_occurred_at', table_name='telemetry_events'
    )
    op.drop_index(
        'ix_telemetry_events_event_type', table_name='telemetry_events'
    )
    op.drop_index('ix_telemetry_events_hasn_id', table_name='telemetry_events')
    op.drop_table('telemetry_events')
