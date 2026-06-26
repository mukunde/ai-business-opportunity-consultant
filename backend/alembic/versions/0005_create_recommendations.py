"""create recommendations

Revision ID: 0005_create_recommendations
Revises: 0004_create_score_snapshots
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0005_create_recommendations"
down_revision: str | None = "0004_create_score_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

recommendation_type = sa.Enum(
    "PROCEED",
    "PROCEED_WITH_CONDITIONS",
    "DEFER",
    "DO_NOT_PURSUE",
    name="recommendation_type",
)


def upgrade() -> None:
    op.create_table(
        "recommendations",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "score_snapshot_id",
            GUID(),
            sa.ForeignKey("score_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", recommendation_type, nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recommendations_opportunity_id", "recommendations", ["opportunity_id"])


def downgrade() -> None:
    op.drop_index("ix_recommendations_opportunity_id", table_name="recommendations")
    op.drop_table("recommendations")
    recommendation_type.drop(op.get_bind(), checkfirst=True)
