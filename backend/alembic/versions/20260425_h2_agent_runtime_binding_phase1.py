"""H2 register HASN agent runtime/binding phase-1 revision anchor

Revision ID: 20260425_h2_agent_runtime_binding_phase1
Revises: 20260424_h1_contacts_owner
Create Date: 2026-04-25 09:00:00.000000

HASN S0/S1 agent runtime and binding schema assets are maintained as
codegen-oriented SQL under `backend/sql/hasn/` plus the additive migration
scripts in that directory. This Alembic revision keeps the managed Alembic
chain continuous after H1 without duplicating those DDL sources.
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260425_h2_agent_runtime_binding_phase1'
down_revision = '20260424_h1_contacts_owner'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
