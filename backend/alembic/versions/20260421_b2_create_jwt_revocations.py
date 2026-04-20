"""B2 create jwt_revocations

Revision ID: 20260421_b2_jwt_revoc
Revises: 7f4afe9adcf8
Create Date: 2026-04-21 03:35:00.000000

Creates `jwt_revocations` table for M1 移动端 POST /api/v1/auth/logout.

Source: docs/架构设计/移动端/05-凭据与安全详细设计.md §16.1
"""
from alembic import op
import sqlalchemy as sa
import backend.common.model  # noqa: F401


# revision identifiers, used by Alembic.
revision = '20260421_b2_jwt_revoc'
down_revision = '7f4afe9adcf8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'jwt_revocations',
        sa.Column(
            'jti',
            sa.String(length=64),
            primary_key=True,
            nullable=False,
            comment='JWT 唯一标识 (M1 复用 session_uuid)',
        ),
        sa.Column(
            'user_id',
            sa.BigInteger(),
            nullable=False,
            server_default='0',
            comment='吊销对应的用户 ID',
        ),
        sa.Column(
            'revoked_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment='吊销时间',
        ),
        sa.Column(
            'expires_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='原 JWT exp 时间 (便于清理)',
        ),
        comment='JWT 吊销记录 (B2)',
    )
    op.create_index(
        'ix_jwt_revocations_user_id',
        'jwt_revocations',
        ['user_id'],
        unique=False,
    )


def downgrade():
    op.drop_index('ix_jwt_revocations_user_id', table_name='jwt_revocations')
    op.drop_table('jwt_revocations')
