"""API tests for the persistent context graph (Epic 3), driven by FakeLLM."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.context.enrichment import enrich_semantics
from app.interview.llm import ContextElement, InferredContradiction, InferredGraph
from app.models.context import ContextNode, ContextNodeType, Contradiction
from app.models.opportunity import Opportunity


def _create_opportunity(client: TestClient) -> str:
    return client.post("/opportunities", json={"title": "Support Automation"}).json()["id"]


def _start(client: TestClient, opp_id: str) -> None:
    client.post(
        f"/opportunities/{opp_id}/interview",
        json={"message": "We receive too many support emails."},
    )


def test_context_empty_before_interview(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    body = client.get(f"/opportunities/{opp_id}/context").json()
    assert body["nodes"] == []
    assert body["evidence"] == []
    assert body["completeness"] is None


def test_context_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.get("/opportunities/00000000-0000-0000-0000-000000000000/context")
    assert resp.status_code == 404


def test_context_after_first_answer(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)
    client.post(f"/opportunities/{opp_id}/continue", json={"answer": "3000 per week"})

    body = client.get(f"/opportunities/{opp_id}/context").json()
    types = [n["type"] for n in body["nodes"]]
    assert types.count("FACT") == 1
    assert types.count("UNKNOWN") == 3
    assert types.count("ASSUMPTION") == 1
    assert len(body["evidence"]) == 1
    assert body["evidence"][0]["type"] == "USER_STATEMENT"
    assert body["completeness"]["overall_score"] == 0.25
    assert body["completeness"]["business_context_score"] == 0.5


def test_context_complete_after_full_interview(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)
    for answer in ["3000 per week", "5 minutes", "2 years history", "Jane, ops lead"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})

    body = client.get(f"/opportunities/{opp_id}/context").json()
    types = [n["type"] for n in body["nodes"]]
    assert types.count("FACT") == 4
    assert types.count("UNKNOWN") == 0
    assert len(body["evidence"]) == 4
    c = body["completeness"]
    assert c["overall_score"] == 1.0
    assert c["business_context_score"] == 1.0
    assert c["process_understanding_score"] == 1.0
    assert c["data_readiness_score"] == 1.0
    assert c["roi_readiness_score"] == 1.0

    # A FACT node references the evidence that produced it.
    fact = next(n for n in body["nodes"] if n["type"] == "FACT")
    assert fact["source_id"] is not None


def test_semantic_relationships_inferred_on_completion(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)
    for answer in ["3000 per week", "5 minutes", "2 years history", "Jane, ops lead"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})

    body = client.get(f"/opportunities/{opp_id}/context").json()
    rels = body["relationships"]
    # FakeLLM hubs the 4 facts + 1 assumption onto the first node: 4 SUPPORTS edges.
    assert len(rels) == 4
    assert {r["relation_type"] for r in rels} == {"SUPPORTS"}
    node_ids = {n["id"] for n in body["nodes"]}
    assert all(r["source_node_id"] in node_ids and r["target_node_id"] in node_ids for r in rels)
    assert body["contradictions"] == []


def test_relationships_absent_before_completion(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)
    client.post(f"/opportunities/{opp_id}/continue", json={"answer": "3000 per week"})

    # Enrichment only runs on the structuring turn, not mid-interview.
    assert client.get(f"/opportunities/{opp_id}/context").json()["relationships"] == []


class _ContradictingLLM:
    """Stub that flags the first two elements as conflicting (the FakeLLM never does)."""

    def infer_relationships(self, elements: list[ContextElement]) -> InferredGraph:
        return InferredGraph(
            contradictions=[
                InferredContradiction(
                    node_a_key=elements[0].key,
                    node_b_key=elements[1].key,
                    explanation="3000/week cannot be handled in 5 minutes each.",
                )
            ]
        )


def test_enrich_persists_contradiction_with_explanation(db_session: Session) -> None:
    opp = Opportunity(title="Conflict case")
    db_session.add(opp)
    db_session.flush()
    for label, value in [("Business Volume", "3000/wk"), ("Average Handling Time", "5 min")]:
        db_session.add(
            ContextNode(
                opportunity_id=opp.id,
                type=ContextNodeType.FACT,
                label=label,
                description=value,
            )
        )
    db_session.flush()

    enrich_semantics(db_session, opp.id, _ContradictingLLM())
    db_session.flush()  # test session has autoflush off; persist the pending rows

    rows = list(
        db_session.execute(
            select(Contradiction).where(Contradiction.opportunity_id == opp.id)
        ).scalars()
    )
    assert len(rows) == 1
    assert rows[0].description == "3000/week cannot be handled in 5 minutes each."
    assert rows[0].node_a_id is not None and rows[0].node_b_id is not None
