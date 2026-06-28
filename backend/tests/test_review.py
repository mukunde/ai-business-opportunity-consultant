"""API tests for the human review decision (Epic 8), driven by FakeLLM."""

from fastapi.testclient import TestClient


def _opp(client: TestClient) -> str:
    return client.post("/opportunities", json={"title": "Support Automation"}).json()["id"]


def _run_to_recommendation(client: TestClient, opp_id: str) -> None:
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    for answer in ["3000/wk", "5 min", "2y history", "Jane"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})
    client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )
    client.post(f"/opportunities/{opp_id}/recommendation")


def test_review_requires_recommendation(client: TestClient) -> None:
    opp_id = _opp(client)
    resp = client.post(f"/opportunities/{opp_id}/review", json={"decision": "APPROVE"})
    assert resp.status_code == 409


def test_review_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.post(
        "/opportunities/00000000-0000-0000-0000-000000000000/review",
        json={"decision": "APPROVE"},
    )
    assert resp.status_code == 404


def test_get_review_before_decision_404(client: TestClient) -> None:
    opp_id = _opp(client)
    assert client.get(f"/opportunities/{opp_id}/review").status_code == 404


def test_approve_sets_status_and_records(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_recommendation(client, opp_id)

    resp = client.post(
        f"/opportunities/{opp_id}/review",
        json={"decision": "APPROVE", "note": "Strong fit, go."},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["decision"] == "APPROVE"
    assert body["note"] == "Strong fit, go."

    assert client.get(f"/opportunities/{opp_id}").json()["status"] == "APPROVED"
    assert client.get(f"/opportunities/{opp_id}/review").json()["decision"] == "APPROVE"


def test_reject_sets_status(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_recommendation(client, opp_id)

    client.post(f"/opportunities/{opp_id}/review", json={"decision": "REJECT"})
    assert client.get(f"/opportunities/{opp_id}").json()["status"] == "REJECTED"


def test_invalid_decision_422(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_recommendation(client, opp_id)
    resp = client.post(f"/opportunities/{opp_id}/review", json={"decision": "MAYBE"})
    assert resp.status_code == 422
