"""The Opportunity ORM model.

Mirrors entity 1 of Backend Schema v1. An Opportunity is the root aggregate:
interview sessions, the context graph, scores and recommendations all hang off
it in later slices.
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


class OpportunityStatus(enum.StrEnum):
    """Lifecycle state of an opportunity (Backend Schema v1, entity 1)."""

    DRAFT = "DRAFT"
    INTERVIEW_ACTIVE = "INTERVIEW_ACTIVE"
    STRUCTURED = "STRUCTURED"
    SCORING = "SCORING"
    RECOMMENDED = "RECOMMENDED"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Opportunity(Base):
    """A business opportunity being evaluated."""

    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    business_area: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[OpportunityStatus] = mapped_column(
        SAEnum(OpportunityStatus, name="opportunity_status"),
        nullable=False,
        default=OpportunityStatus.DRAFT,
    )
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
