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

# Only substantive nodes can carry semantic relationships; gaps (UNKNOWN) cannot.
_CONNECTABLE = (ContextNodeType.FACT, ContextNodeType.ASSUMPTION)


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

    graph = llm.infer_relationships(elements)

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
        if node_a is None or node_b is None or node_a == node_b:
            continue
        db.add(
            Contradiction(
                opportunity_id=opportunity_id,
                node_a_id=node_a,
                node_b_id=node_b,
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
