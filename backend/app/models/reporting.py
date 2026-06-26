"""Reporting ORM models (Backend Schema v1, entities 11 and 12).

Decision-ready outputs rendered as Markdown. ``version_id`` is reserved for
Phase 2 versioning and stays null for now.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ExecutiveSummary(Base):
    """One-page, decision-oriented summary (entity 11)."""

    __tablename__ = "executive_summaries"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    version_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class DetailedAssessment(Base):
    """Full structured breakdown of the evaluation (entity 12)."""

    __tablename__ = "detailed_assessments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    version_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
