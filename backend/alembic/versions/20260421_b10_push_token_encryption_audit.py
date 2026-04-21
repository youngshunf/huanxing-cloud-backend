"""B10 push_tokens token BYTEA 加密 + push_token_audit 表

Revision ID: 20260421_b10_push_audit
Revises: 20260421_b8_telemetry_events
Create Date: 2026-04-21 14:50:00.000000

1. 给 `push_tokens.token` 列从 VARCHAR(512) 改为 BYTEA (应用层 Fernet 加密后的密文).
   M1 pre-prod 尚无生产数据, 使用 USING 表达式把已有 TEXT 值转成等价 BYTEA
   (即使留在表里也是旧格式的未加密 bytes, 部署后需手工清理 / 走 B4 POST 覆盖).
2. 新增 `push_token_audit` 表: 记录 push_tokens 每次 INSERT/UPDATE/DELETE 的元数据
   (push_token_id / hasn_id / device_id / channel / action / occurred_at) —
   详细规范见 docs/架构设计/移动端/04-推送触达与后台运行模型详细设计.md §13.2。

无 push_token_audit 外键约束 (push_tokens 删除后审计保留元数据; FK CASCADE 会
反向消除证据链)。只在 push_token_id + hasn_id 上建索引用于热路径查询。
"""
import sqlalchemy as sa

from alembic import op

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260421_b10_push_audit'
down_revision = '20260421_b8_telemetry_events'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. push_token_audit 审计表
    op.create_table(
        'push_token_audit',
        sa.Column(
            'id',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
            comment='主键 ID',
        ),
        sa.Column(
            'push_token_id',
            sa.BigInteger(),
            nullable=True,
            comment='关联 push_tokens.id (DELETE 时保留元数据)',
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
            comment='设备 device_id',
        ),
        sa.Column(
            'channel',
            sa.String(length=16),
            nullable=False,
            server_default='umeng_push',
            comment='推送通道',
        ),
        sa.Column(
            'action',
            sa.String(length=16),
            nullable=False,
            server_default='INSERT',
            comment='INSERT/UPDATE/DELETE',
        ),
        sa.Column(
            'occurred_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='事件时间',
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
        comment='push_tokens 读写审计表 (B10)',
    )
    op.create_index(
        'ix_push_token_audit_hasn_id', 'push_token_audit', ['hasn_id'], unique=False,
    )
    op.create_index(
        'ix_push_token_audit_push_token_id',
        'push_token_audit',
        ['push_token_id'],
        unique=False,
    )

    # 2. push_tokens.token  VARCHAR(512) → BYTEA (LargeBinary)
    # M1 pre-prod 无真实数据; 保守 USING 把旧明文转字节保留. 新 INSERT 走 App 层加密.
    op.alter_column(
        'push_tokens',
        'token',
        existing_type=sa.String(length=512),
        type_=sa.LargeBinary(),
        existing_nullable=False,
        existing_server_default='',
        server_default=None,
        postgresql_using="convert_to(coalesce(token, ''), 'UTF8')",
    )


def downgrade() -> None:
    # 回退 token 列到 VARCHAR(512); BYTEA → text (UTF-8 解码, 仅适用于 upgrade 后
    # 未写入加密数据的情况).
    op.alter_column(
        'push_tokens',
        'token',
        existing_type=sa.LargeBinary(),
        type_=sa.String(length=512),
        existing_nullable=False,
        existing_server_default=None,
        server_default='',
        postgresql_using="convert_from(token, 'UTF8')",
    )

    op.drop_index('ix_push_token_audit_push_token_id', table_name='push_token_audit')
    op.drop_index('ix_push_token_audit_hasn_id', table_name='push_token_audit')
    op.drop_table('push_token_audit')
