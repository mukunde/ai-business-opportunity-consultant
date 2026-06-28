"""create discovery_sessions and discovered_opportunities

Revision ID: 0009_create_discovery
Revises: 0008_create_opportunity_versions
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0009_create_discovery"
down_revision: str | None = "0008_create_opportunity_versions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

discovery_status = sa.Enum("ACTIVE", "COMPLETED", name="discovery_status")


def upgrade() -> None:
    op.create_table(
        "discovery_sessions",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", discovery_status, nullable=False),
        sa.Column("working_state", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "discovered_opportunities",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            GUID(),
            sa.ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("target_pain_point", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("promoted_opportunity_id", GUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_discovered_opportunities_session_id",
        "discovered_opportunities",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_discovered_opportunities_session_id", table_name="discovered_opportunities"
    )
    op.drop_table("discovered_opportunities")
    op.drop_table("discovery_sessions")
    discovery_status.drop(op.get_bind(), checkfirst=True)
