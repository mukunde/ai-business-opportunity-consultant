"""Project interview working state into the persistent context graph.

The context graph is a projection of the interview state, so projecting is
idempotent: wipe the opportunity's nodes/evidence/completeness and rebuild from
the current state. Runs inside the interview transaction (no commit here).
"""

import uuid

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.interview.state import SLOT_KEYS, SLOT_LABELS, OpportunityState
from app.models.context import (
    ContextCompleteness,
    ContextNode,
    ContextNodeType,
    Evidence,
    EvidenceType,
)

# Which context slots feed each completeness dimension (entity 8).
DIMENSION_SLOTS: dict[str, list[str]] = {
    "business_context": ["business_volume", "process_owner"],
    "process_understanding": ["handling_time"],
    "data_readiness": ["data_availability"],
    "roi_readiness": ["business_volume", "handling_time"],
}


def compute_completeness(context: dict[str, str]) -> dict[str, float]:
    """Fraction of each dimension's slots that are filled, plus the overall."""

    def dimension(slots: list[str]) -> float:
        return sum(1 for slot in slots if context.get(slot)) / len(slots)

    overall = sum(1 for slot in SLOT_KEYS if context.get(slot)) / len(SLOT_KEYS)
    return {
        "business_context_score": dimension(DIMENSION_SLOTS["business_context"]),
        "process_understanding_score": dimension(DIMENSION_SLOTS["process_understanding"]),
        "data_readiness_score": dimension(DIMENSION_SLOTS["data_readiness"]),
        "roi_readiness_score": dimension(DIMENSION_SLOTS["roi_readiness"]),
        "overall_score": overall,
    }


def project_context(db: Session, opportunity_id: uuid.UUID, state: OpportunityState) -> None:
    """Rebuild the opportunity's context graph from the interview state."""
    context = state.get("context", {})
    assumptions = state.get("assumptions", [])

    # Idempotent wipe (deleting nodes cascades their relationships).
    db.execute(delete(ContextNode).where(ContextNode.opportunity_id == opportunity_id))
    db.execute(delete(Evidence).where(Evidence.opportunity_id == opportunity_id))
    db.execute(
        delete(ContextCompleteness).where(ContextCompleteness.opportunity_id == opportunity_id)
    )

    # FACT nodes for filled slots, each backed by a USER_STATEMENT evidence.
    for slot in SLOT_KEYS:
        value = context.get(slot)
        if not value:
            continue
        evidence = Evidence(
            opportunity_id=opportunity_id,
            type=EvidenceType.USER_STATEMENT,
            content=value,
            confidence=1.0,
        )
        db.add(evidence)
        db.flush()  # assign evidence.id for the node's source_id
        db.add(
            ContextNode(
                opportunity_id=opportunity_id,
                type=ContextNodeType.FACT,
                label=SLOT_LABELS[slot],
                description=value,
                confidence=1.0,
                source_id=evidence.id,
            )
        )

    # UNKNOWN nodes for the slots still missing.
    for slot in SLOT_KEYS:
        if context.get(slot):
            continue
        db.add(
            ContextNode(
                opportunity_id=opportunity_id,
                type=ContextNodeType.UNKNOWN,
                label=SLOT_LABELS[slot],
                confidence=0.0,
            )
        )

    # ASSUMPTION nodes.
    for assumption in assumptions:
        db.add(
            ContextNode(
                opportunity_id=opportunity_id,
                type=ContextNodeType.ASSUMPTION,
                label=assumption,
                confidence=0.5,
            )
        )

    db.add(ContextCompleteness(opportunity_id=opportunity_id, **compute_completeness(context)))
