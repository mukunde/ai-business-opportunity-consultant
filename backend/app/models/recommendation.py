"""Recommendation ORM model (Backend Schema v1, entity 10).

The system's decision for an opportunity, derived from a score snapshot.
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


class RecommendationType(enum.StrEnum):
    """Decision outcomes (Backend Schema v1, entity 10; Appflow flow 8)."""

    PROCEED = "PROCEED"
    PROCEED_WITH_CONDITIONS = "PROCEED_WITH_CONDITIONS"
    DEFER = "DEFER"
    DO_NOT_PURSUE = "DO_NOT_PURSUE"


class Recommendation(Base):
    """A decision-ready recommendation for one opportunity."""

    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    score_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("score_snapshots.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[RecommendationType] = mapped_column(
        SAEnum(RecommendationType, name="recommendation_type"), nullable=False
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
