import pytest

from app.services import report_service

REPORT_FIXTURE = {
    "period": {"month": 4, "year": 2026, "label": "Avril 2026"},
    "kpi": {
        "total_incidents": 32,
        "resolved": 21,
        "open": 11,
        "resolution_rate_pct": 65.6,
        "avg_mttr_minutes": 138,
        "network_availability_pct": 93.8,
        "critical_localities": 3,
        "recurrent_nodes": 7,
        "off_hours_detected": 7,
    },
    "vs_previous_month": {"incidents_delta": 4, "availability_delta": -1.2},
    "top_localities": [
        {
            "locality": "Dédougou",
            "region": "Boucle du Mouhoun",
            "total_incidents": 9,
            "availability_pct": 91.2,
        }
    ],
    "top_nodes": [],
    "recurrent_nodes": [
        {"code": "DED-001", "name": "DREP Dédougou", "total_incidents": 5}
    ],
}


def test_render_pdf_produces_pdf_bytes():
    content = report_service.render_pdf(REPORT_FIXTURE)
    assert content.startswith(b"%PDF")
    assert len(content) > 500


def test_render_docx_produces_docx_bytes():
    content = report_service.render_docx(REPORT_FIXTURE)
    # A .docx is a ZIP container
    assert content[:2] == b"PK"
    assert len(content) > 1000


def test_render_docx_handles_no_recurrent_nodes():
    report = {**REPORT_FIXTURE, "recurrent_nodes": []}
    content = report_service.render_docx(report)
    assert content[:2] == b"PK"
