from datetime import datetime
from types import SimpleNamespace

import pytest

from app.routes import incidents as incidents_routes
from app.routes import kpi as kpi_routes
from app.routes import report as report_routes
from tests.conftest import API_KEY_HEADERS

SUMMARY = {
    "period": {"month": 4, "year": 2026, "label": "Avril 2026"},
    "kpi": {"total_incidents": 32},
    "vs_previous_month": {"incidents_delta": 4},
}


@pytest.fixture(autouse=True)
def no_cache(monkeypatch):
    """Redis is not available in tests; make the cache an explicit no-op."""
    monkeypatch.setattr("app.services.cache_service.get_cached", lambda key: None)
    monkeypatch.setattr("app.services.cache_service.set_cached", lambda key, value, ttl=None: None)
    monkeypatch.setattr("app.services.cache_service.invalidate_prefix", lambda prefix: None)


@pytest.fixture
def fake_summary(monkeypatch):
    monkeypatch.setattr(kpi_routes.kpi_service, "get_summary", lambda db, m, y: SUMMARY)


# --- Auth on read endpoints (spec §10.1) ---


def test_kpi_summary_requires_auth(client):
    response = client.get("/api/kpi/summary", params={"month": 4, "year": 2026})
    assert response.status_code == 401


def test_kpi_summary_allows_any_role(client, analyst_headers, fake_summary):
    response = client.get(
        "/api/kpi/summary", params={"month": 4, "year": 2026}, headers=analyst_headers
    )
    assert response.status_code == 200
    assert response.json() == SUMMARY


def test_sla_requires_auth(client):
    assert client.get("/api/sla", params={"month": 4, "year": 2026}).status_code == 401


def test_alerts_requires_auth(client):
    assert client.get("/api/alerts/open").status_code == 401


def test_compare_endpoint(client, admin_headers, monkeypatch):
    payload = {"period": SUMMARY["period"], "kpi": SUMMARY["kpi"], "comparisons": []}
    monkeypatch.setattr(kpi_routes.kpi_service, "get_comparison", lambda db, m, y: payload)
    response = client.get(
        "/api/kpi/compare", params={"month": 4, "year": 2026}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == payload


# --- Report auth: JWT or static API key ---


def test_report_accepts_api_key(client, monkeypatch):
    monkeypatch.setattr(
        report_routes.report_service, "build_report_data", lambda db, m, y: SUMMARY
    )
    response = client.get(
        "/api/report/monthly",
        params={"month": 4, "year": 2026},
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 200


def test_report_rejects_anonymous(client):
    response = client.get("/api/report/monthly", params={"month": 4, "year": 2026})
    assert response.status_code == 401


# --- RBAC on write actions ---

FAKE_INCIDENT = SimpleNamespace(
    id=4821,
    node_id=12,
    itop_ticket_id=None,
    shift="auto",
    created_at=datetime(2026, 5, 17, 3, 22, 1),
    severity="critical",
    status="open",
    detected_at=datetime(2026, 5, 17, 3, 22, 0),
    description="Perte de connectivité",
)


@pytest.fixture
def fake_incident_service(monkeypatch):
    monkeypatch.setattr(
        incidents_routes.incident_service,
        "resolve_incident",
        lambda db, incident_id, resolved_at, notes: FAKE_INCIDENT,
    )
    monkeypatch.setattr(
        incidents_routes.incident_service,
        "acknowledge_incident",
        lambda db, incident_id, acknowledged_at: FAKE_INCIDENT,
    )


def test_analyst_cannot_resolve(client, analyst_headers, fake_incident_service):
    response = client.patch(
        "/api/incidents/4821/resolve", json={}, headers=analyst_headers
    )
    assert response.status_code == 403


def test_noc_agent_can_acknowledge(client, noc_agent_headers, fake_incident_service):
    response = client.patch(
        "/api/incidents/4821/acknowledge", json={}, headers=noc_agent_headers
    )
    assert response.status_code == 200


def test_admin_can_resolve(client, admin_headers, fake_incident_service):
    response = client.patch("/api/incidents/4821/resolve", json={}, headers=admin_headers)
    assert response.status_code == 200


# --- Ingest webhook ---

INGEST_PAYLOAD = {
    "external_id": "zabbix-alert-48291",
    "source_tool": "zabbix",
    "node_code": "DED-001",
    "severity": "critical",
    "status": "open",
    "detected_at": "2026-05-17T03:22:00Z",
    "description": "Perte de connectivité",
}


@pytest.fixture
def fake_ingest(monkeypatch):
    published = []
    notified = []
    monkeypatch.setattr(
        incidents_routes.incident_service, "ingest_incident", lambda db, payload: FAKE_INCIDENT
    )
    monkeypatch.setattr(
        incidents_routes.incident_service,
        "get_node_by_code",
        lambda db, code: SimpleNamespace(code=code, name="DREP Dédougou"),
    )
    monkeypatch.setattr(
        incidents_routes.alert_broadcaster, "publish_alert", published.append
    )
    monkeypatch.setattr(
        incidents_routes.notification_service,
        "notify_critical_incident",
        lambda *args: notified.append(args),
    )
    return published, notified


def test_ingest_requires_api_key(client, fake_ingest):
    assert client.post("/api/incidents/ingest", json=INGEST_PAYLOAD).status_code == 401


def test_ingest_rejects_jwt_of_dashboard_user(client, admin_headers, fake_ingest):
    response = client.post(
        "/api/incidents/ingest", json=INGEST_PAYLOAD, headers=admin_headers
    )
    assert response.status_code == 401


def test_ingest_creates_broadcasts_and_notifies(client, fake_ingest):
    published, notified = fake_ingest
    response = client.post(
        "/api/incidents/ingest", json=INGEST_PAYLOAD, headers=API_KEY_HEADERS
    )
    assert response.status_code == 201
    assert response.json()["incident_id"] == 4821

    assert len(published) == 1
    assert published[0]["node_code"] == "DED-001"
    assert published[0]["severity"] == "critical"

    # critical severity → SMS/email background task fired
    assert len(notified) == 1
    assert notified[0][1] == "DED-001"


def test_ingest_non_critical_does_not_notify(client, fake_ingest, monkeypatch):
    published, notified = fake_ingest
    medium_incident = SimpleNamespace(**{**FAKE_INCIDENT.__dict__, "severity": "medium"})
    monkeypatch.setattr(
        incidents_routes.incident_service, "ingest_incident", lambda db, payload: medium_incident
    )
    payload = {**INGEST_PAYLOAD, "severity": "medium"}
    response = client.post("/api/incidents/ingest", json=payload, headers=API_KEY_HEADERS)
    assert response.status_code == 201
    assert len(published) == 1
    assert notified == []


def test_ingest_validates_source_tool(client, fake_ingest):
    payload = {**INGEST_PAYLOAD, "source_tool": "solarwinds"}
    response = client.post("/api/incidents/ingest", json=payload, headers=API_KEY_HEADERS)
    assert response.status_code == 422
