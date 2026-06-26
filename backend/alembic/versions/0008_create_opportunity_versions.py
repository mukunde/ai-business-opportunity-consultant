"""create opportunity_versions

Revision ID: 0008_create_opportunity_versions
Revises: 0007_contradiction_description
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0008_create_opportunity_versions"
down_revision: str | None = "0007_contradiction_description"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "opportunity_versions",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_opportunity_versions_opportunity_id",
        "opportunity_versions",
        ["opportunity_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_opportunity_versions_opportunity_id", table_name="opportunity_versions"
    )
    op.drop_table("opportunity_versions")
