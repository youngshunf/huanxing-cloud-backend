"""H3 register HASN memory namespace revision anchor

Revision ID: 20260523_h3_memory_namespace_revisions
Revises: 20260425_h2_agent_runtime_binding_phase1
Create Date: 2026-05-23 09:00:00.000000

HASN memory namespace revision assets are maintained as codegen-oriented SQL
under `backend/sql/hasn/`. This Alembic revision keeps the managed Alembic
chain continuous after H2 without duplicating that DDL source.
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260523_h3_memory_namespace_revisions'
down_revision = '20260425_h2_agent_runtime_binding_phase1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
