"""Interview ORM models (Backend Schema v1, entities 3 and 4).

An InterviewSession is the adaptive qualification workshop attached to an
Opportunity; ConversationTurn stores every exchange. ``working_state`` holds the
serialized engine state so a turn-based web interview can be reloaded and
replayed between HTTP calls (the TRD requires everything be replayable). Epic 3
will normalize this working state into the persistent context graph.
"""

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class InterviewStatus(enum.StrEnum):
    """Lifecycle of an interview session (Backend Schema v1, entity 3)."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class TurnRole(enum.StrEnum):
    """Author of a conversation turn (Backend Schema v1, entity 4)."""

    USER = "USER"
    CONSULTANT = "CONSULTANT"


class InterviewSession(Base):
    """A qualification workshop for one opportunity."""

    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[InterviewStatus] = mapped_column(
        SAEnum(InterviewStatus, name="interview_status"),
        nullable=False,
        default=InterviewStatus.ACTIVE,
    )
    # Serialized engine state (known context slots, unknowns, completeness, ...).
    working_state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    turns: Mapped[list["ConversationTurn"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ConversationTurn.created_at",
    )


class ConversationTurn(Base):
    """A single message in an interview session."""

    __tablename__ = "conversation_turns"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[TurnRole] = mapped_column(SAEnum(TurnRole, name="turn_role"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # Why the consultant asked what it asked (explainability, Appflow principle).
    reasoning_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    session: Mapped[InterviewSession] = relationship(back_populates="turns")
