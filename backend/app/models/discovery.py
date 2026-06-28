"""Discovery ORM models (ADR 0004).

A DiscoverySession explores a business/process upstream of any opportunity. Its
working state (interview context, pain points, ingested signals) lives in a JSON
column, mirroring InterviewSession. On completion it yields DiscoveredOpportunity
candidates, each promotable into a real Opportunity.
"""

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class DiscoveryStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class DiscoverySession(Base):
    """An upstream business/process discovery workshop."""

    __tablename__ = "discovery_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DiscoveryStatus] = mapped_column(
        SAEnum(DiscoveryStatus, name="discovery_status"),
        nullable=False,
        default=DiscoveryStatus.ACTIVE,
    )
    working_state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DiscoveredOpportunity(Base):
    """A candidate AI opportunity surfaced by a discovery session."""

    __tablename__ = "discovered_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("discovery_sessions.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    target_pain_point: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    # Set once the candidate has been promoted into a real Opportunity.
    promoted_opportunity_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
