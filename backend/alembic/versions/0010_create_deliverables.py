"""create deliverables

Revision ID: 0010_create_deliverables
Revises: 0009_create_discovery
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0010_create_deliverables"
down_revision: str | None = "0009_create_discovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

deliverable_kind = sa.Enum(
    "CONDENSED_BRIEF",
    "IMPLEMENTATION_ROADMAP",
    "PRD",
    "TRD",
    "UIUX",
    "BACKEND_SCHEMA",
    "APPFLOW",
    name="deliverable_kind",
)


def upgrade() -> None:
    op.create_table(
        "deliverables",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", deliverable_kind, nullable=False),
        sa.Column("markdown_content", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_deliverables_opportunity_id", "deliverables", ["opportunity_id"])


def downgrade() -> None:
    op.drop_index("ix_deliverables_opportunity_id", table_name="deliverables")
    op.drop_table("deliverables")
    deliverable_kind.drop(op.get_bind(), checkfirst=True)
