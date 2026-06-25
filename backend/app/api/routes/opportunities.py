"""HTTP routes for the Opportunity resource (Phase 1, Epic 1)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityRead,
    OpportunityUpdate,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _get_or_404(db: Session, opportunity_id: uuid.UUID) -> Opportunity:
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opportunity


@router.post("", response_model=OpportunityRead, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate, db: Session = Depends(get_db)
) -> OpportunityRead:
    """Create a new opportunity (starts in DRAFT)."""
    opportunity = crud.opportunity.create_opportunity(db, payload)
    return OpportunityRead.model_validate(opportunity)


@router.get("", response_model=list[OpportunityRead])
def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[OpportunityRead]:
    """List opportunities, newest first."""
    rows = crud.opportunity.list_opportunities(db, skip=skip, limit=limit)
    return [OpportunityRead.model_validate(row) for row in rows]


@router.get("/{opportunity_id}", response_model=OpportunityRead)
def get_opportunity(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> OpportunityRead:
    """Fetch a single opportunity by id."""
    opportunity = _get_or_404(db, opportunity_id)
    return OpportunityRead.model_validate(opportunity)


@router.patch("/{opportunity_id}", response_model=OpportunityRead)
def update_opportunity(
    opportunity_id: uuid.UUID,
    payload: OpportunityUpdate,
    db: Session = Depends(get_db),
) -> OpportunityRead:
    """Partially update an opportunity."""
    opportunity = _get_or_404(db, opportunity_id)
    updated = crud.opportunity.update_opportunity(db, opportunity, payload)
    return OpportunityRead.model_validate(updated)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    """Delete an opportunity."""
    opportunity = _get_or_404(db, opportunity_id)
    crud.opportunity.delete_opportunity(db, opportunity)
