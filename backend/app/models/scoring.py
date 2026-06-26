"""Scoring ORM model (Backend Schema v1, entity 9).

A ScoreSnapshot is an immutable evaluation of an opportunity at a point in time.
``version_id`` is reserved for Phase 2 versioning and stays null for now.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ScoreSnapshot(Base):
    """A scoring snapshot for one opportunity."""

    __tablename__ = "score_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    version_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)

    roi_score: Mapped[float] = mapped_column(Float, nullable=False)
    impact_score: Mapped[float] = mapped_column(Float, nullable=False)
    feasibility_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    strategic_alignment_score: Mapped[float] = mapped_column(Float, nullable=False)
    time_to_value_score: Mapped[float] = mapped_column(Float, nullable=False)
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
