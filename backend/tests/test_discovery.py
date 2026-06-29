"""API tests for the upstream Discovery flow (ADR 0004), driven by FakeLLM."""

from fastapi.testclient import TestClient

_ANSWERS = [
    "Mobilier sur mesure",
    "Reduire le cycle de vente",
    "Devis client",
    "Visite, devis, relance",
]


def _start(client: TestClient) -> str:
    return client.post(
        "/discovery", json={"title": "Service ADV", "message": "On vend des cuisines."}
    ).json()["id"]


def _complete(client: TestClient, sid: str) -> dict:
    body: dict = {}
    for answer in _ANSWERS:
        body = client.post(f"/discovery/{sid}/continue", json={"answer": answer}).json()
    return body


def test_start_asks_first_question(client: TestClient) -> None:
    resp = client.post(
        "/discovery", json={"title": "Service ADV", "message": "On vend des cuisines."}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "ACTIVE"
    assert body["done"] is False
    assert body["completeness"] == 0.0
    assert body["next_question"]  # a first question was asked


def test_full_discovery_completes_and_detects(client: TestClient) -> None:
    sid = _start(client)
    body = _complete(client, sid)
    assert body["status"] == "COMPLETED"
    assert body["done"] is True
    assert body["completeness"] == 1.0
    assert len(body["context"]) == 4
    assert body["pain_points"]  # at least one irritant surfaced

    candidates = client.get(f"/discovery/{sid}/opportunities").json()
    assert len(candidates) >= 1
    assert candidates[0]["target_pain_point"]
    assert candidates[0]["promoted_opportunity_id"] is None


def test_continue_after_completion_409(client: TestClient) -> None:
    sid = _start(client)
    _complete(client, sid)
    resp = client.post(f"/discovery/{sid}/continue", json={"answer": "extra"})
    assert resp.status_code == 409


def test_ingest_signal_feeds_pain_points(client: TestClient) -> None:
    sid = _start(client)
    body = client.post(
        f"/discovery/{sid}/signal",
        json={"label": "Volume mails", "value": "3000/semaine non traites"},
    ).json()
    assert len(body["signals"]) == 1
    assert any("Volume mails" in p for p in body["pain_points"])


def test_promote_candidate_creates_opportunity(client: TestClient) -> None:
    sid = _start(client)
    _complete(client, sid)
    candidate = client.get(f"/discovery/{sid}/opportunities").json()[0]

    resp = client.post(f"/discovery/{sid}/opportunities/{candidate['id']}/promote")
    assert resp.status_code == 201
    opp = resp.json()
    assert opp["status"] == "DRAFT"
    assert opp["business_area"] == "Service ADV"

    # The candidate is now linked; a second promote is rejected.
    again = client.post(f"/discovery/{sid}/opportunities/{candidate['id']}/promote")
    assert again.status_code == 409
    # And the opportunity is retrievable in the normal pipeline.
    assert client.get(f"/opportunities/{opp['id']}").status_code == 200


def test_list_sessions(client: TestClient) -> None:
    assert client.get("/discovery").json() == []
    sid = _start(client)
    sessions = client.get("/discovery").json()
    assert len(sessions) == 1
    assert sessions[0]["id"] == sid
    assert sessions[0]["status"] == "ACTIVE"


def test_connector_flow_ingest_then_detect(client: TestClient) -> None:
    """Signals fed without an interview, then detection surfaces candidates."""
    sid = _start(client)
    client.post(
        f"/discovery/{sid}/signal",
        json={"label": "Volume mails SAV", "value": "3000/semaine non traites"},
    )
    client.post(
        f"/discovery/{sid}/signal",
        json={"label": "Recopie manuelle", "value": "devis ressaisis dans l'ERP"},
    )

    body = client.post(f"/discovery/{sid}/detect").json()
    assert body["status"] == "COMPLETED"
    assert body["done"] is True

    candidates = client.get(f"/discovery/{sid}/opportunities").json()
    assert len(candidates) >= 2  # one per ingested signal (FakeLLM)

    # Detecting again on a completed session is rejected.
    assert client.post(f"/discovery/{sid}/detect").status_code == 409


def test_discovery_unknown_session_404(client: TestClient) -> None:
    assert client.get("/discovery/00000000-0000-0000-0000-000000000000").status_code == 404
