"""Review ORM model (Phase 2, Epic 8 - ADR 0006).

An append-only human sign-off on an opportunity's recommendation: each decision is
a row, so the verdict history stays auditable (the traceability principle).
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ReviewDecision(enum.StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class Review(Base):
    """A human approve/reject decision on a recommended opportunity."""

    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[ReviewDecision] = mapped_column(
        SAEnum(ReviewDecision, name="review_decision"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
