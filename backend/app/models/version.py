"""OpportunityVersion ORM model (Backend Schema v1, entity 2).

An immutable snapshot of an opportunity's assessment at a point in time. The
schema's lone ``summary`` text is generalized into a denormalized ``snapshot``
JSON so two versions can be compared field by field (Epic 7 "Comparison"),
without re-deriving from the context graph, which is rebuilt every interview
turn. See ADR 0003.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


class OpportunityVersion(Base):
    """A frozen snapshot of an opportunity's assessment."""

    __tablename__ = "opportunity_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # Optional human label for why this version was cut (e.g. "after cost data").
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Denormalized assessment at cut time (see app.schemas.version.AssessmentSnapshot).
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
