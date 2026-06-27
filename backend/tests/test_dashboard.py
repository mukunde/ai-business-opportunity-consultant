"""API tests for the dashboard summary endpoint (Epic 9), driven by FakeLLM."""

from fastapi.testclient import TestClient


def _opp(client: TestClient, title: str = "Support Automation") -> str:
    return client.post("/opportunities", json={"title": title}).json()["id"]


def _run_to_recommendation(client: TestClient, opp_id: str) -> None:
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    for answer in ["3000/wk", "5 min", "2y history", "Jane"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})
    client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )
    client.post(f"/opportunities/{opp_id}/recommendation")


def test_summary_empty(client: TestClient) -> None:
    assert client.get("/opportunities/summary").json() == []


def test_summary_bare_opportunity_has_null_signals(client: TestClient) -> None:
    opp_id = _opp(client)
    row = next(r for r in client.get("/opportunities/summary").json() if r["id"] == opp_id)
    assert row["status"] == "DRAFT"
    assert row["final_score"] is None
    assert row["recommendation_type"] is None
    assert row["completeness"] is None


def test_summary_reflects_score_and_recommendation(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_recommendation(client, opp_id)

    row = next(r for r in client.get("/opportunities/summary").json() if r["id"] == opp_id)
    assert row["final_score"] is not None
    assert row["recommendation_type"] == "PROCEED"
    assert row["completeness"] == 1.0
    assert row["status"] == "RECOMMENDED"


def test_summary_newest_first(client: TestClient) -> None:
    first = _opp(client, "First")
    second = _opp(client, "Second")
    ids = [r["id"] for r in client.get("/opportunities/summary").json()]
    assert ids.index(second) < ids.index(first)
