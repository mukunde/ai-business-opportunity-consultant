"""API tests for the persistent context graph (Epic 3), driven by FakeLLM."""

from fastapi.testclient import TestClient


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
