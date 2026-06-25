"""Persistence operations for Opportunity, isolated from the HTTP layer."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate


def create_opportunity(db: Session, data: OpportunityCreate) -> Opportunity:
    """Insert a new opportunity in DRAFT status and return it."""
    opportunity = Opportunity(
        title=data.title,
        business_area=data.business_area,
        owner_id=data.owner_id,
    )
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


def get_opportunity(db: Session, opportunity_id: uuid.UUID) -> Opportunity | None:
    """Return one opportunity by id, or None if it does not exist."""
    return db.get(Opportunity, opportunity_id)


def list_opportunities(db: Session, *, skip: int = 0, limit: int = 50) -> Sequence[Opportunity]:
    """Return a page of opportunities, newest first."""
    stmt = select(Opportunity).order_by(Opportunity.created_at.desc()).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def update_opportunity(
    db: Session, opportunity: Opportunity, data: OpportunityUpdate
) -> Opportunity:
    """Apply a partial update (only fields explicitly set on the payload)."""
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(opportunity, field, value)
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    return opportunity


def delete_opportunity(db: Session, opportunity: Opportunity) -> None:
    """Delete an opportunity."""
    db.delete(opportunity)
    db.commit()
