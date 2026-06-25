"""create interview_sessions and conversation_turns

Revision ID: 0002_create_interview_tables
Revises: 0001_create_opportunities
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0002_create_interview_tables"
down_revision: str | None = "0001_create_opportunities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

interview_status = sa.Enum("ACTIVE", "PAUSED", "COMPLETED", name="interview_status")
turn_role = sa.Enum("USER", "CONSULTANT", name="turn_role")


def upgrade() -> None:
    op.create_table(
        "interview_sessions",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", interview_status, nullable=False),
        sa.Column("working_state", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_interview_sessions_opportunity_id",
        "interview_sessions",
        ["opportunity_id"],
    )

    op.create_table(
        "conversation_turns",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            GUID(),
            sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", turn_role, nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("reasoning_trace", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_conversation_turns_session_id",
        "conversation_turns",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversation_turns_session_id", table_name="conversation_turns")
    op.drop_table("conversation_turns")
    op.drop_index("ix_interview_sessions_opportunity_id", table_name="interview_sessions")
    op.drop_table("interview_sessions")
    turn_role.drop(op.get_bind(), checkfirst=True)
    interview_status.drop(op.get_bind(), checkfirst=True)
