"""create context graph tables

Revision ID: 0003_create_context_graph
Revises: 0002_create_interview_tables
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0003_create_context_graph"
down_revision: str | None = "0002_create_interview_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

context_node_type = sa.Enum(
    "FACT",
    "UNKNOWN",
    "ASSUMPTION",
    "CONSTRAINT",
    "KPI",
    "RISK",
    "STAKEHOLDER",
    name="context_node_type",
)
relation_type = sa.Enum("SUPPORTS", "CONTRADICTS", "DEPENDS_ON", "REQUIRES", name="relation_type")
evidence_type = sa.Enum("USER_STATEMENT", "DOCUMENT", "METRIC", "CALCULATION", name="evidence_type")
contradiction_status = sa.Enum("OPEN", "RESOLVED", name="contradiction_status")


def upgrade() -> None:
    op.create_table(
        "evidence",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", evidence_type, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_opportunity_id", "evidence", ["opportunity_id"])

    op.create_table(
        "context_nodes",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", context_node_type, nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_id", GUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_context_nodes_opportunity_id", "context_nodes", ["opportunity_id"])

    op.create_table(
        "context_relationships",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "source_node_id",
            GUID(),
            sa.ForeignKey("context_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_node_id",
            GUID(),
            sa.ForeignKey("context_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("relation_type", relation_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_context_relationships_source_node_id",
        "context_relationships",
        ["source_node_id"],
    )

    op.create_table(
        "contradictions",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("node_a_id", GUID(), nullable=True),
        sa.Column("node_b_id", GUID(), nullable=True),
        sa.Column("status", contradiction_status, nullable=False),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_contradictions_opportunity_id", "contradictions", ["opportunity_id"])

    op.create_table(
        "context_completeness",
        sa.Column("id", GUID(), primary_key=True, nullable=False),
        sa.Column(
            "opportunity_id",
            GUID(),
            sa.ForeignKey("opportunities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("business_context_score", sa.Float(), nullable=False),
        sa.Column("process_understanding_score", sa.Float(), nullable=False),
        sa.Column("data_readiness_score", sa.Float(), nullable=False),
        sa.Column("roi_readiness_score", sa.Float(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_context_completeness_opportunity_id",
        "context_completeness",
        ["opportunity_id"],
    )


def downgrade() -> None:
    op.drop_table("context_completeness")
    op.drop_table("contradictions")
    op.drop_table("context_relationships")
    op.drop_table("context_nodes")
    op.drop_table("evidence")
    contradiction_status.drop(op.get_bind(), checkfirst=True)
    evidence_type.drop(op.get_bind(), checkfirst=True)
    relation_type.drop(op.get_bind(), checkfirst=True)
    context_node_type.drop(op.get_bind(), checkfirst=True)
