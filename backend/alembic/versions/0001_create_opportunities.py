"""create opportunities table

Revision ID: 0001_create_opportunities
Revises:
Create Date: 2026-06-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0001_create_opportunities"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

opportunity_status = sa.Enum(
    "DRAFT",
    "INTERVIEW_ACTIVE",
    "STRUCTURED",
    "SCORING",
    "RECOMMENDED",
    "REVIEW",
    name="opportunity_status",
)


def upgrade() -> None:
    op.create_table(
        "opportunities",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("business_area", sa.String(length=255), nullable=True),
        sa.Column("status", opportunity_status, nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False),
        sa.Column("owner_id", GUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("opportunities")
    opportunity_status.drop(op.get_bind(), checkfirst=True)
