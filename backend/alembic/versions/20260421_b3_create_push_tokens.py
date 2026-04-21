"""B3 create push_tokens

Revision ID: 20260421_b3_push_tokens
Revises: 20260421_b2_jwt_revoc
Create Date: 2026-04-21 12:30:00.000000

Creates `push_tokens` table for M1 移动端推送通道 (友盟 U-Push)。

Source: docs/架构设计/移动端/04-推送触达与后台运行模型详细设计.md §5.3。
M1 决策: channel 字段枚举固定 'umeng_push' (友盟已内聚 6 厂商); FCM 延期到 M2。
"""
import sqlalchemy as sa

from alembic import op

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260421_b3_push_tokens'
down_revision = '20260421_b2_jwt_revoc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'push_tokens',
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
            'device_id',
            sa.String(length=64),
            nullable=False,
            server_default='',
            comment='唯一设备标识',
        ),
        sa.Column(
            'channel',
            sa.String(length=16),
            nullable=False,
            server_default='umeng_push',
            comment="推送通道 (M1 固定 'umeng_push')",
        ),
        sa.Column(
            'token',
            sa.String(length=512),
            nullable=False,
            server_default='',
            comment='通道 push token',
        ),
        sa.Column(
            'registered_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='首次注册时间',
        ),
        sa.Column(
            'last_seen_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='最后一次注册/心跳时间',
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
        comment='M1 移动端推送 Token 表 (友盟 U-Push) [B3]',
    )
    op.create_unique_constraint(
        'uq_push_tokens_hasn_device_channel',
        'push_tokens',
        ['hasn_id', 'device_id', 'channel'],
    )
    op.create_index(
        'ix_push_tokens_hasn_id',
        'push_tokens',
        ['hasn_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_push_tokens_hasn_id', table_name='push_tokens')
    op.drop_constraint(
        'uq_push_tokens_hasn_device_channel',
        'push_tokens',
        type_='unique',
    )
    op.drop_table('push_tokens')
