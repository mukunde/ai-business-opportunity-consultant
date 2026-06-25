"""Context graph ORM models (Backend Schema v1, entities 5 to 8).

Stored relationally in Postgres as an adjacency list (see ADR 0001): typed nodes,
a node-to-node edge table, supporting evidence, contradictions, and a completeness
snapshot. The graph is a projection of the interview state and is rebuilt
idempotently each turn.
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ContextNodeType(enum.StrEnum):
    FACT = "FACT"
    UNKNOWN = "UNKNOWN"
    ASSUMPTION = "ASSUMPTION"
    CONSTRAINT = "CONSTRAINT"
    KPI = "KPI"
    RISK = "RISK"
    STAKEHOLDER = "STAKEHOLDER"


class RelationType(enum.StrEnum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    DEPENDS_ON = "DEPENDS_ON"
    REQUIRES = "REQUIRES"


class EvidenceType(enum.StrEnum):
    USER_STATEMENT = "USER_STATEMENT"
    DOCUMENT = "DOCUMENT"
    METRIC = "METRIC"
    CALCULATION = "CALCULATION"


class ContradictionStatus(enum.StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class Evidence(Base):
    """Supporting evidence for a context element (entity 6)."""

    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[EvidenceType] = mapped_column(
        SAEnum(EvidenceType, name="evidence_type"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class ContextNode(Base):
    """A typed element of context (entity 5.1)."""

    __tablename__ = "context_nodes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[ContextNodeType] = mapped_column(
        SAEnum(ContextNodeType, name="context_node_type"), nullable=False
    )
    label: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Logical reference to the Evidence row that produced this node (no DB FK to
    # avoid a circular dependency; evidence and nodes share a lifecycle).
    source_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class ContextRelationship(Base):
    """A typed edge between two context nodes (entity 5.2)."""

    __tablename__ = "context_relationships"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("context_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("context_nodes.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[RelationType] = mapped_column(
        SAEnum(RelationType, name="relation_type"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class Contradiction(Base):
    """A tracked conflict between two context elements (entity 7)."""

    __tablename__ = "contradictions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    # Logical references to nodes (no FK: contradictions outlive node rebuilds).
    node_a_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    node_b_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    status: Mapped[ContradictionStatus] = mapped_column(
        SAEnum(ContradictionStatus, name="contradiction_status"),
        nullable=False,
        default=ContradictionStatus.OPEN,
    )
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class ContextCompleteness(Base):
    """Dimensional completeness snapshot (entity 8). First-class, not derived."""

    __tablename__ = "context_completeness"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    business_context_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    process_understanding_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    data_readiness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    roi_readiness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
