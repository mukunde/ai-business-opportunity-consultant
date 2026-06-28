"""Discovery orchestration (ADR 0004).

A lightweight adaptive loop (no LangGraph: thin enough to stay in plain functions)
that reuses the LLMClient abstraction. The interview is one producer of signals;
``ingest_signal`` is the seam a future mail connector plugs into. On completion the
detector surfaces candidate opportunities; ``promote`` turns one into a real
Opportunity that enters the existing qualification pipeline.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.discovery.slots import (
    DISCOVERY_SLOT_KEYS,
    DISCOVERY_SLOT_LABELS,
    DISCOVERY_SLOT_REASONS,
)
from app.interview.llm import LLMClient
from app.models.discovery import (
    DiscoveredOpportunity,
    DiscoverySession,
    DiscoveryStatus,
)
from app.models.opportunity import Opportunity

State = dict[str, Any]


def _initial_state(message: str) -> State:
    return {
        "raw_input": message,
        "latest_answer": "",
        "context": {},
        "pain_points": [],
        "signals": [],
        "missing": list(DISCOVERY_SLOT_KEYS),
        "completeness": 0.0,
        "next_question": None,
        "done": False,
        "turns": [{"role": "USER", "message": message}],
    }


def _run_turn(llm: LLMClient, state: State) -> State:
    """Fold the latest answer into context, then ask the next gap or finish."""
    answer = state.get("latest_answer", "").strip()
    if answer:
        extracted = llm.extract_discovery(
            state.get("raw_input", ""), answer, state.get("context", {})
        )
        context = dict(state.get("context", {}))
        for key in DISCOVERY_SLOT_KEYS:
            value = getattr(extracted, key, None)
            if value:
                context[key] = value
        state["context"] = context
        state["pain_points"] = list(state.get("pain_points", [])) + list(extracted.pain_points)

    missing = [k for k in DISCOVERY_SLOT_KEYS if not state.get("context", {}).get(k)]
    state["missing"] = missing
    state["completeness"] = (len(DISCOVERY_SLOT_KEYS) - len(missing)) / len(DISCOVERY_SLOT_KEYS)
    if missing:
        slot = missing[0]
        state["next_question"] = llm.next_question_for(
            DISCOVERY_SLOT_LABELS[slot],
            DISCOVERY_SLOT_REASONS[slot],
            state.get("raw_input", ""),
            state.get("context", {}),
        )
        state["done"] = False
        state["turns"].append({"role": "CONSULTANT", "message": state["next_question"]})
    else:
        state["next_question"] = None
        state["done"] = True
    state["latest_answer"] = ""  # consumed
    return state


def _detect_and_persist(db: Session, session: DiscoverySession, llm: LLMClient) -> None:
    state = session.working_state
    detection = llm.detect_opportunities(state.get("context", {}), state.get("pain_points", []))
    for candidate in detection.opportunities:
        db.add(
            DiscoveredOpportunity(
                session_id=session.id,
                title=candidate.title,
                target_pain_point=candidate.target_pain_point,
                rationale=candidate.rationale,
            )
        )


def start_discovery(db: Session, title: str, message: str, llm: LLMClient) -> DiscoverySession:
    """Open a discovery session and ask the first question."""
    state = _run_turn(llm, _initial_state(message))
    session = DiscoverySession(
        title=title,
        status=DiscoveryStatus.ACTIVE,
        working_state=state,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def continue_discovery(
    db: Session, session: DiscoverySession, answer: str, llm: LLMClient
) -> DiscoverySession:
    """Process one answer; on completion, detect candidate opportunities."""
    state = dict(session.working_state)
    state["turns"] = list(state.get("turns", [])) + [{"role": "USER", "message": answer}]
    state["latest_answer"] = answer
    session.working_state = _run_turn(llm, state)

    if session.working_state.get("done"):
        session.status = DiscoveryStatus.COMPLETED
        session.completed_at = datetime.now(UTC)
        _detect_and_persist(db, session, llm)

    db.commit()
    db.refresh(session)
    return session


def ingest_signal(
    db: Session, session: DiscoverySession, label: str, value: str
) -> DiscoverySession:
    """Push a signal into the session without an interview (the connector seam).

    Stored as a signal and folded into the pain points so the detector sees it,
    exactly as the future mail connector will feed irritants in bulk.
    """
    state = dict(session.working_state)
    state["signals"] = list(state.get("signals", [])) + [{"label": label, "value": value}]
    state["pain_points"] = list(state.get("pain_points", [])) + [f"{label}: {value}"]
    session.working_state = state
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: uuid.UUID) -> DiscoverySession | None:
    return db.get(DiscoverySession, session_id)


def list_candidates(db: Session, session_id: uuid.UUID) -> list[DiscoveredOpportunity]:
    stmt = (
        select(DiscoveredOpportunity)
        .where(DiscoveredOpportunity.session_id == session_id)
        .order_by(DiscoveredOpportunity.created_at)
    )
    return list(db.execute(stmt).scalars())


def get_candidate(
    db: Session, session_id: uuid.UUID, candidate_id: uuid.UUID
) -> DiscoveredOpportunity | None:
    stmt = select(DiscoveredOpportunity).where(
        DiscoveredOpportunity.id == candidate_id,
        DiscoveredOpportunity.session_id == session_id,
    )
    return db.execute(stmt).scalars().first()


def promote(
    db: Session, session: DiscoverySession, candidate: DiscoveredOpportunity
) -> Opportunity:
    """Turn a candidate into a real Opportunity entering the qualification pipeline."""
    opportunity = Opportunity(title=candidate.title, business_area=session.title)
    db.add(opportunity)
    db.flush()  # assign opportunity.id
    candidate.promoted_opportunity_id = opportunity.id
    db.commit()
    db.refresh(opportunity)
    return opportunity
