"""create score_snapshots

Revision ID: 0004_create_score_snapshots
Revises: 0003_create_context_graph
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0004_create_score_snapshots"
down_revision: str | None = "0003_create_context_graph"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "score_snapshots",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_id", GUID(), nullable=True),
        sa.Column("roi_score", sa.Float(), nullable=False),
        sa.Column("impact_score", sa.Float(), nullable=False),
        sa.Column("feasibility_score", sa.Float(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("strategic_alignment_score", sa.Float(), nullable=False),
        sa.Column("time_to_value_score", sa.Float(), nullable=False),
        sa.Column("final_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_score_snapshots_opportunity_id", "score_snapshots", ["opportunity_id"])


def downgrade() -> None:
    op.drop_index("ix_score_snapshots_opportunity_id", table_name="score_snapshots")
    op.drop_table("score_snapshots")
