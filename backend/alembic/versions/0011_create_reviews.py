"""create reviews and add APPROVED/REJECTED opportunity statuses

Revision ID: 0011_create_reviews
Revises: 0010_create_deliverables
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0011_create_reviews"
down_revision: str | None = "0010_create_deliverables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

review_decision = sa.Enum("APPROVE", "REJECT", name="review_decision")


def upgrade() -> None:
    # Two terminal lifecycle states for the human verdict (PostgreSQL 12+ allows
    # ADD VALUE inside the migration transaction; the values are not used here).
    op.execute("ALTER TYPE opportunity_status ADD VALUE IF NOT EXISTS 'APPROVED'")
    op.execute("ALTER TYPE opportunity_status ADD VALUE IF NOT EXISTS 'REJECTED'")

    op.create_table(
        "reviews",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("decision", review_decision, nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reviews_opportunity_id", "reviews", ["opportunity_id"])


def downgrade() -> None:
    op.drop_index("ix_reviews_opportunity_id", table_name="reviews")
    op.drop_table("reviews")
    review_decision.drop(op.get_bind(), checkfirst=True)
    # The added opportunity_status enum values are left in place (PostgreSQL has no
    # safe DROP VALUE); harmless if unused.
