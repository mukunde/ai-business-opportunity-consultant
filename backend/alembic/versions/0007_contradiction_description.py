"""add description column to contradictions

Revision ID: 0007_contradiction_description
Revises: 0006_create_reporting_tables
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007_contradiction_description"
down_revision: str | None = "0006_create_reporting_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("contradictions", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("contradictions", "description")
