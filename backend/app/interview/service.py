"""Interview orchestration: bridge the LangGraph engine and the database.

The database is the source of truth. Each call reloads the working state from the
session, runs one graph turn, persists the new state, records the conversation
turns, and advances the opportunity lifecycle.
"""

import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.interview.graph import run_turn
from app.interview.llm import LLMClient
from app.interview.state import from_dict, initial_state
from app.models.interview import (
    ConversationTurn,
    InterviewSession,
    InterviewStatus,
    TurnRole,
)
from app.models.opportunity import Opportunity, OpportunityStatus


def assistant_message(state: Mapping[str, Any]) -> str:
    """The consultant's visible message for the current state."""
    if state.get("done"):
        problem = state.get("problem_statement") or ""
        summary = state.get("summary") or ""
        return f"{problem}\n\n{summary}".strip()
    return state.get("next_question") or ""


def get_active_session(db: Session, opportunity_id: uuid.UUID) -> InterviewSession | None:
    """Return the opportunity's active (or paused) interview session, if any."""
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.opportunity_id == opportunity_id)
        .where(InterviewSession.status != InterviewStatus.COMPLETED)
        .order_by(InterviewSession.started_at.desc())
    )
    return db.execute(stmt).scalars().first()


def _threshold() -> float:
    return get_settings().context_completeness_threshold


def _record_turn(
    db: Session,
    session: InterviewSession,
    role: TurnRole,
    message: str,
    reasoning: str | None = None,
) -> None:
    db.add(
        ConversationTurn(
            session_id=session.id,
            role=role,
            message=message,
            reasoning_trace=reasoning,
        )
    )


def start_interview(
    db: Session, opportunity: Opportunity, message: str, llm: LLMClient
) -> InterviewSession:
    """Create a session, run the opening turn, and ask the first question."""
    state = initial_state(str(opportunity.id), raw_input=message)

    session = InterviewSession(
        opportunity_id=opportunity.id,
        status=InterviewStatus.ACTIVE,
        working_state=dict(state),
    )
    db.add(session)
    db.flush()  # assign session.id for the turns below

    _record_turn(db, session, TurnRole.USER, message)

    state = run_turn(llm, state, _threshold())
    session.working_state = dict(state)
    _record_turn(
        db,
        session,
        TurnRole.CONSULTANT,
        assistant_message(state),
        state.get("reasoning"),
    )

    opportunity.status = OpportunityStatus.INTERVIEW_ACTIVE
    db.commit()
    db.refresh(session)
    return session


def continue_interview(
    db: Session, session: InterviewSession, answer: str, llm: LLMClient
) -> InterviewSession:
    """Process one user answer and produce the next consultant turn."""
    _record_turn(db, session, TurnRole.USER, answer)

    state = from_dict(session.working_state)
    state["latest_answer"] = answer
    state = run_turn(llm, state, _threshold())
    session.working_state = dict(state)

    _record_turn(
        db,
        session,
        TurnRole.CONSULTANT,
        assistant_message(state),
        state.get("reasoning"),
    )

    opportunity = db.get(Opportunity, session.opportunity_id)
    if state.get("done"):
        session.status = InterviewStatus.COMPLETED
        session.completed_at = datetime.now(UTC)
        if opportunity is not None:
            opportunity.status = OpportunityStatus.STRUCTURED

    db.commit()
    db.refresh(session)
    return session
