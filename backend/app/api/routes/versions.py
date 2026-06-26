"""HTTP routes for opportunity versioning (Phase 2, Epic 7)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.schemas.version import VersionCreate, VersionRead
from app.versioning import service

router = APIRouter(prefix="/opportunities", tags=["versioning"])


@router.post(
    "/{opportunity_id}/versions",
    response_model=VersionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_version(
    opportunity_id: uuid.UUID,
    payload: VersionCreate | None = None,
    db: Session = Depends(get_db),
) -> VersionRead:
    """Freeze the current assessment as a new numbered version."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    note = payload.note if payload else None
    version = service.create_version(db, opportunity, note)
    return VersionRead.model_validate(version)


@router.get("/{opportunity_id}/versions", response_model=list[VersionRead])
def list_versions(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> list[VersionRead]:
    """Return the opportunity's version history, newest first."""
    if crud.opportunity.get_opportunity(db, opportunity_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    versions = service.list_versions(db, opportunity_id)
    return [VersionRead.model_validate(v) for v in versions]


@router.get("/{opportunity_id}/versions/{version_id}", response_model=VersionRead)
def get_version(
    opportunity_id: uuid.UUID, version_id: uuid.UUID, db: Session = Depends(get_db)
) -> VersionRead:
    """Return a single version of an opportunity."""
    version = service.get_version(db, opportunity_id, version_id)
    if version is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Version not found")
    return VersionRead.model_validate(version)
