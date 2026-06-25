"""HTTP routes for the adaptive interview (Phase 1, Epic 2)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.interview import service
from app.interview.llm import LLMClient, get_llm
from app.models.interview import InterviewSession
from app.schemas.interview import (
    ContextView,
    ContinueRequest,
    InterviewSessionRead,
    InterviewStartRequest,
    InterviewTurnResponse,
    TurnRead,
)

router = APIRouter(prefix="/opportunities", tags=["interview"])


def _context_view(session: InterviewSession) -> ContextView:
    state = session.working_state or {}
    return ContextView(
        context=state.get("context", {}),
        missing=state.get("missing", []),
        assumptions=state.get("assumptions", []),
        completeness=state.get("completeness", 0.0),
    )


def _turn_response(session: InterviewSession) -> InterviewTurnResponse:
    state = session.working_state or {}
    return InterviewTurnResponse(
        session_id=session.id,
        status=session.status,
        assistant_message=service.assistant_message(state),
        done=bool(state.get("done")),
        context=_context_view(session),
    )


@router.post(
    "/{opportunity_id}/interview",
    response_model=InterviewTurnResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_interview(
    opportunity_id: uuid.UUID,
    payload: InterviewStartRequest,
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm),
) -> InterviewTurnResponse:
    """Start the qualification interview for an opportunity."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    if service.get_active_session(db, opportunity_id) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An interview is already in progress")
    session = service.start_interview(db, opportunity, payload.message, llm)
    return _turn_response(session)


@router.post("/{opportunity_id}/continue", response_model=InterviewTurnResponse)
def continue_interview(
    opportunity_id: uuid.UUID,
    payload: ContinueRequest,
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm),
) -> InterviewTurnResponse:
    """Submit an answer and get the consultant's next move."""
    session = service.get_active_session(db, opportunity_id)
    if session is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "No active interview for this opportunity")
    session = service.continue_interview(db, session, payload.answer, llm)
    return _turn_response(session)


@router.get("/{opportunity_id}/interview", response_model=InterviewSessionRead)
def get_interview(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> InterviewSessionRead:
    """Fetch the latest interview session and its transcript."""
    session = service.get_active_session(db, opportunity_id)
    if session is None:
        # fall back to the most recent (possibly completed) session
        from sqlalchemy import select

        stmt = (
            select(InterviewSession)
            .where(InterviewSession.opportunity_id == opportunity_id)
            .order_by(InterviewSession.started_at.desc())
        )
        session = db.execute(stmt).scalars().first()
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No interview found")
    return InterviewSessionRead(
        session_id=session.id,
        opportunity_id=session.opportunity_id,
        status=session.status,
        context=_context_view(session),
        turns=[TurnRead.model_validate(t) for t in session.turns],
    )
