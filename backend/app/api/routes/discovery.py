"""HTTP routes for upstream Discovery (Phase 2, ADR 0004)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.discovery import service
from app.interview.llm import LLMClient, get_llm
from app.models.discovery import DiscoverySession, DiscoveryStatus
from app.schemas.discovery import (
    DiscoveredOpportunityRead,
    DiscoveryAnswer,
    DiscoverySessionRead,
    DiscoveryStart,
    SignalIngest,
)
from app.schemas.opportunity import OpportunityRead

router = APIRouter(prefix="/discovery", tags=["discovery"])


def _read(session: DiscoverySession) -> DiscoverySessionRead:
    s = session.working_state
    return DiscoverySessionRead(
        id=session.id,
        title=session.title,
        status=session.status,
        completeness=s.get("completeness", 0.0),
        next_question=s.get("next_question"),
        done=s.get("done", False),
        context=s.get("context", {}),
        pain_points=s.get("pain_points", []),
        signals=s.get("signals", []),
        turns=s.get("turns", []),
    )


def _get_or_404(db: Session, session_id: uuid.UUID) -> DiscoverySession:
    session = service.get_session(db, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Discovery session not found")
    return session


@router.post("", response_model=DiscoverySessionRead, status_code=status.HTTP_201_CREATED)
def start_discovery(
    payload: DiscoveryStart,
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm),
) -> DiscoverySessionRead:
    """Open a discovery session and ask the first question."""
    return _read(service.start_discovery(db, payload.title, payload.message, llm))


@router.post("/{session_id}/continue", response_model=DiscoverySessionRead)
def continue_discovery(
    session_id: uuid.UUID,
    payload: DiscoveryAnswer,
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm),
) -> DiscoverySessionRead:
    """Process one answer; on completion, candidate opportunities are detected."""
    session = _get_or_404(db, session_id)
    if session.status == DiscoveryStatus.COMPLETED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Discovery already completed")
    return _read(service.continue_discovery(db, session, payload.answer, llm))


@router.get("/{session_id}", response_model=DiscoverySessionRead)
def get_discovery(session_id: uuid.UUID, db: Session = Depends(get_db)) -> DiscoverySessionRead:
    """Return the current state of a discovery session."""
    return _read(_get_or_404(db, session_id))


@router.post("/{session_id}/signal", response_model=DiscoverySessionRead)
def ingest_signal(
    session_id: uuid.UUID,
    payload: SignalIngest,
    db: Session = Depends(get_db),
) -> DiscoverySessionRead:
    """Push a signal into the session without an interview (connector seam)."""
    session = _get_or_404(db, session_id)
    return _read(service.ingest_signal(db, session, payload.label, payload.value))


@router.get("/{session_id}/opportunities", response_model=list[DiscoveredOpportunityRead])
def list_candidates(
    session_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[DiscoveredOpportunityRead]:
    """List the candidate opportunities surfaced by this discovery session."""
    _get_or_404(db, session_id)
    return [
        DiscoveredOpportunityRead.model_validate(c)
        for c in service.list_candidates(db, session_id)
    ]


@router.post(
    "/{session_id}/opportunities/{candidate_id}/promote",
    response_model=OpportunityRead,
    status_code=status.HTTP_201_CREATED,
)
def promote_candidate(
    session_id: uuid.UUID,
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> OpportunityRead:
    """Promote a candidate into a real Opportunity (enters qualification)."""
    session = _get_or_404(db, session_id)
    candidate = service.get_candidate(db, session_id, candidate_id)
    if candidate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")
    if candidate.promoted_opportunity_id is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Candidate already promoted")
    return OpportunityRead.model_validate(service.promote(db, session, candidate))
