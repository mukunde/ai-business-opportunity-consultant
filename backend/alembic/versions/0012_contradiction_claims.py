"""record the verbatim statements behind a transcript-sourced contradiction

Revision ID: 0012_contradiction_claims
Revises: 0011_create_reviews
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0012_contradiction_claims"
down_revision: str | None = "0011_create_reviews"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A contradiction found in the interview transcript has no pair of context
    # nodes to point at, so it carries the two conflicting statements instead.
    op.add_column("contradictions", sa.Column("claim_a", sa.Text(), nullable=True))
    op.add_column("contradictions", sa.Column("claim_b", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("contradictions", "claim_b")
    op.drop_column("contradictions", "claim_a")
