"""legacy baseline (pre-alembic state stamp)

Revision ID: 7f4afe9adcf8
Revises:
Create Date: 2026-04-21 03:30:00.000000

Placeholder no-op representing the state of the DB before alembic was actively
managed (legacy `sql/migrations/*.sql` era).  Exists so `alembic upgrade head`
works both on DBs currently stamped at this revision (via a prior `alembic
stamp` operation) and on fresh DBs.

No DDL executed in upgrade/downgrade.
"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401
import backend.common.model  # noqa: F401

# revision identifiers, used by Alembic.
revision = '7f4afe9adcf8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
