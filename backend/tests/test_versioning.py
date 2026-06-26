"""API tests for opportunity versioning (Epic 7), driven by FakeLLM."""

from fastapi.testclient import TestClient


def _opp(client: TestClient) -> str:
    return client.post("/opportunities", json={"title": "Support Automation"}).json()["id"]


def _run_to_score(client: TestClient, opp_id: str, *, impact: int = 8) -> None:
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    for answer in ["3000/wk", "5 min", "2y history", "Jane"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})
    client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": impact, "ease": 6, "strategic_alignment": 9},
    )


def test_create_version_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.post("/opportunities/00000000-0000-0000-0000-000000000000/versions")
    assert resp.status_code == 404


def test_list_versions_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.get("/opportunities/00000000-0000-0000-0000-000000000000/versions")
    assert resp.status_code == 404


def test_first_version_snapshots_current_state(client: TestClient) -> None:
    opp_id = _opp(client)
    resp = client.post(f"/opportunities/{opp_id}/versions", json={"note": "baseline"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["version_number"] == 1
    assert body["note"] == "baseline"
    # A bare opportunity degrades gracefully: no score or recommendation yet.
    assert body["snapshot"]["title"] == "Support Automation"
    assert body["snapshot"]["score"] is None
    assert body["snapshot"]["recommendation_type"] is None

    assert client.get(f"/opportunities/{opp_id}").json()["current_version"] == 1


def test_version_captures_score_and_recommendation(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_score(client, opp_id)
    client.post(f"/opportunities/{opp_id}/recommendation")

    snap = client.post(f"/opportunities/{opp_id}/versions").json()["snapshot"]
    assert snap["score"]["final_score"] is not None
    assert snap["recommendation_type"] == "PROCEED"
    assert len(snap["facts"]) == 4


def test_versions_increment_and_list_newest_first(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_score(client, opp_id, impact=9)
    v1 = client.post(f"/opportunities/{opp_id}/versions").json()

    # Re-score with weaker inputs, then cut a second version: a comparison case.
    client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 2, "ease": 2, "strategic_alignment": 2},
    )
    v2 = client.post(f"/opportunities/{opp_id}/versions").json()

    assert v1["version_number"] == 1
    assert v2["version_number"] == 2
    assert v2["snapshot"]["score"]["final_score"] < v1["snapshot"]["score"]["final_score"]
    assert client.get(f"/opportunities/{opp_id}").json()["current_version"] == 2

    history = client.get(f"/opportunities/{opp_id}/versions").json()
    assert [v["version_number"] for v in history] == [2, 1]


def test_get_single_version(client: TestClient) -> None:
    opp_id = _opp(client)
    created = client.post(f"/opportunities/{opp_id}/versions").json()
    fetched = client.get(f"/opportunities/{opp_id}/versions/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]

    missing = client.get(f"/opportunities/{opp_id}/versions/00000000-0000-0000-0000-000000000000")
    assert missing.status_code == 404
