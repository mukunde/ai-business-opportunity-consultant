"""LLM-driven semantic enrichment of the context graph.

The deterministic projector (``projection.py``) builds the FACT/UNKNOWN/ASSUMPTION
nodes. This step reasons *across* them: it asks the model to infer typed edges
(SUPPORTS / DEPENDS_ON / REQUIRES) and contradictions, then persists them.

It runs once per interview, on the structuring turn, so the model reasons over the
complete context with a single call (ADR 0002). The model never sees database
UUIDs: each node is handed an opaque key (``n0``, ``n1``, ...) it echoes back.
"""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.interview.llm import ContextElement, LLMClient
from app.models.context import (
    ContextNode,
    ContextNodeType,
    ContextRelationship,
    Contradiction,
    RelationType,
)
from app.models.interview import ConversationTurn, InterviewSession

# Only substantive nodes can carry semantic relationships; gaps (UNKNOWN) cannot.
_CONNECTABLE = (ContextNodeType.FACT, ContextNodeType.ASSUMPTION)


def _transcript(db: Session, opportunity_id: uuid.UUID) -> str:
    """Render the interview as it was said, for tensions the slots cannot hold.

    A context slot keeps a single value, so a user who contradicts themselves
    overwrites the earlier statement: it survives only here (ADR 0008).
    """
    turns = db.execute(
        select(ConversationTurn)
        .join(InterviewSession, InterviewSession.id == ConversationTurn.session_id)
        .where(InterviewSession.opportunity_id == opportunity_id)
        .order_by(ConversationTurn.created_at)
    ).scalars()
    return "\n".join(f"{turn.role.value}: {turn.message}" for turn in turns)


def enrich_semantics(db: Session, opportunity_id: uuid.UUID, llm: LLMClient) -> None:
    """Infer and persist semantic edges and contradictions for the opportunity."""
    db.flush()  # ensure projector-added nodes are queryable below

    nodes = list(
        db.execute(
            select(ContextNode)
            .where(ContextNode.opportunity_id == opportunity_id)
            .where(ContextNode.type.in_(_CONNECTABLE))
            .order_by(ContextNode.created_at)
        ).scalars()
    )
    # Always clear prior enrichment so the step stays idempotent.
    _clear(db, opportunity_id, [n.id for n in nodes])
    if len(nodes) < 2:
        return

    keymap = {f"n{i}": node.id for i, node in enumerate(nodes)}
    elements = [
        ContextElement(
            key=f"n{i}",
            label=node.label,
            value=node.description or "",
            kind=node.type.value,
        )
        for i, node in enumerate(nodes)
    ]

    graph = llm.infer_relationships(elements, _transcript(db, opportunity_id))

    for rel in graph.relationships:
        source = keymap.get(rel.source_key)
        target = keymap.get(rel.target_key)
        if source is None or target is None or source == target:
            continue  # ignore edges referencing unknown or self keys
        db.add(
            ContextRelationship(
                source_node_id=source,
                target_node_id=target,
                relation_type=RelationType(rel.relation_type),
            )
        )

    for conflict in graph.contradictions:
        node_a = keymap.get(conflict.node_a_key)
        node_b = keymap.get(conflict.node_b_key)
        claim_a = conflict.claim_a.strip()
        claim_b = conflict.claim_b.strip()
        between_nodes = node_a is not None and node_b is not None and node_a != node_b
        between_claims = bool(claim_a) and bool(claim_b) and claim_a != claim_b
        if not between_nodes and not between_claims:
            continue  # ignore conflicts anchored to nothing we can show
        db.add(
            Contradiction(
                opportunity_id=opportunity_id,
                node_a_id=node_a if between_nodes else None,
                node_b_id=node_b if between_nodes else None,
                claim_a=claim_a or None,
                claim_b=claim_b or None,
                description=conflict.explanation,
            )
        )


def _clear(db: Session, opportunity_id: uuid.UUID, node_ids: list[uuid.UUID]) -> None:
    """Drop the previous enrichment (edges out of these nodes, contradictions)."""
    if node_ids:
        db.execute(
            delete(ContextRelationship).where(ContextRelationship.source_node_id.in_(node_ids))
        )
    db.execute(delete(Contradiction).where(Contradiction.opportunity_id == opportunity_id))
