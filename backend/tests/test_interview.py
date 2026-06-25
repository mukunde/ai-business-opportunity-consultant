"""API tests for the adaptive interview engine (Epic 2), driven by FakeLLM."""

from fastapi.testclient import TestClient


def _create_opportunity(client: TestClient) -> str:
    resp = client.post("/opportunities", json={"title": "Support Automation"})
    return resp.json()["id"]


def _start(client: TestClient, opp_id: str) -> dict:
    return client.post(
        f"/opportunities/{opp_id}/interview",
        json={"message": "We receive too many support emails."},
    ).json()


def test_start_asks_first_question(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    resp = client.post(
        f"/opportunities/{opp_id}/interview",
        json={"message": "We receive too many support emails."},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "ACTIVE"
    assert body["done"] is False
    assert body["assistant_message"]  # a question was asked
    assert body["context"]["completeness"] == 0.0
    assert len(body["context"]["missing"]) == 4

    # The opportunity advanced to INTERVIEW_ACTIVE.
    opp = client.get(f"/opportunities/{opp_id}").json()
    assert opp["status"] == "INTERVIEW_ACTIVE"


def test_start_twice_conflicts(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)
    resp = client.post(f"/opportunities/{opp_id}/interview", json={"message": "again"})
    assert resp.status_code == 409


def test_continue_without_session_conflicts(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    resp = client.post(f"/opportunities/{opp_id}/continue", json={"answer": "x"})
    assert resp.status_code == 409


def test_full_interview_reaches_structured(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)

    answers = ["3000 per week", "5 minutes", "yes, 2 years of history", "Jane, ops lead"]
    body: dict = {}
    for answer in answers:
        body = client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer}).json()

    assert body["done"] is True
    assert body["status"] == "COMPLETED"
    assert body["context"]["completeness"] == 1.0
    assert body["context"]["missing"] == []
    assert "Structured problem" in body["assistant_message"]
    # An assumption was captured along the way.
    assert "Requests are repetitive" in body["context"]["assumptions"]

    opp = client.get(f"/opportunities/{opp_id}").json()
    assert opp["status"] == "STRUCTURED"


def test_transcript_records_both_roles(client: TestClient) -> None:
    opp_id = _create_opportunity(client)
    _start(client, opp_id)
    client.post(f"/opportunities/{opp_id}/continue", json={"answer": "3000 per week"})

    resp = client.get(f"/opportunities/{opp_id}/interview")
    assert resp.status_code == 200
    turns = resp.json()["turns"]
    roles = [t["role"] for t in turns]
    assert roles.count("USER") >= 2
    assert roles.count("CONSULTANT") >= 2
