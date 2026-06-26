"""create executive_summaries and detailed_assessments

Revision ID: 0006_create_reporting_tables
Revises: 0005_create_recommendations
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0006_create_reporting_tables"
down_revision: str | None = "0005_create_recommendations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _report_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_id", GUID(), nullable=True),
        sa.Column("markdown_content", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(f"ix_{name}_opportunity_id", name, ["opportunity_id"])


def upgrade() -> None:
    _report_table("executive_summaries")
    _report_table("detailed_assessments")


def downgrade() -> None:
    op.drop_index("ix_detailed_assessments_opportunity_id", table_name="detailed_assessments")
    op.drop_table("detailed_assessments")
    op.drop_index("ix_executive_summaries_opportunity_id", table_name="executive_summaries")
    op.drop_table("executive_summaries")
