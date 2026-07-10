import io

from sqlalchemy.orm import Session

from app.services import kpi_service


def build_report_data(db: Session, month: int, year: int) -> dict:
    summary = kpi_service.get_summary(db, month, year)
    localities = kpi_service.get_localities(db, month, year, limit=10)
    nodes = kpi_service.get_nodes(db, month, year, limit=10)
    recurrent = kpi_service.get_recurrent_nodes(db, month, year)
    return {
        "period": summary["period"],
        "kpi": summary["kpi"],
        "vs_previous_month": summary["vs_previous_month"],
        "top_localities": localities,
        "top_nodes": nodes,
        "recurrent_nodes": recurrent,
    }


def render_pdf(report: dict) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Rapport Mensuel NOC - ANPTIC", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Periode: {report['period']['label']}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Indicateurs cles", ln=True)
    pdf.set_font("Helvetica", "", 11)
    kpi = report["kpi"]
    labels = {
        "total_incidents": "Total incidents",
        "resolved": "Resolus",
        "open": "Ouverts",
        "resolution_rate_pct": "Taux de resolution (%)",
        "avg_mttr_minutes": "MTTR moyen (min)",
        "network_availability_pct": "Disponibilite reseau (%)",
        "critical_localities": "Localites critiques",
        "recurrent_nodes": "Noeuds recurrents",
        "off_hours_detected": "Incidents hors heures ouvrees",
    }
    for key, label in labels.items():
        pdf.cell(0, 7, f"- {label}: {kpi[key]}", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Top localites", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for loc in report["top_localities"]:
        pdf.cell(
            0,
            7,
            f"- {loc['locality']} ({loc['region']}): {loc['total_incidents']} incidents, "
            f"dispo {loc['availability_pct']}%",
            ln=True,
        )

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Noeuds recurrents (>= 3 incidents)", ln=True)
    pdf.set_font("Helvetica", "", 11)
    if report["recurrent_nodes"]:
        for node in report["recurrent_nodes"]:
            pdf.cell(
                0,
                7,
                f"- {node['code']} {node['name']}: {node['total_incidents']} incidents",
                ln=True,
            )
    else:
        pdf.cell(0, 7, "Aucun noeud recurrent ce mois-ci.", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


KPI_LABELS = {
    "total_incidents": "Total incidents",
    "resolved": "Résolus",
    "open": "Ouverts",
    "resolution_rate_pct": "Taux de résolution (%)",
    "avg_mttr_minutes": "MTTR moyen (min)",
    "network_availability_pct": "Disponibilité réseau (%)",
    "critical_localities": "Localités critiques",
    "recurrent_nodes": "Nœuds récurrents",
    "off_hours_detected": "Incidents hors heures ouvrées",
}


def render_docx(report: dict) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_heading("Rapport Mensuel NOC — ANPTIC", level=0)
    doc.add_paragraph(f"Période : {report['period']['label']}")

    doc.add_heading("Indicateurs clés", level=1)
    kpi = report["kpi"]
    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for key, label in KPI_LABELS.items():
        row = table.add_row().cells
        row[0].text = label
        row[1].text = str(kpi[key])

    doc.add_heading("Top localités", level=1)
    for loc in report["top_localities"]:
        doc.add_paragraph(
            f"{loc['locality']} ({loc['region']}) : {loc['total_incidents']} incidents, "
            f"disponibilité {loc['availability_pct']}%",
            style="List Bullet",
        )

    doc.add_heading("Nœuds récurrents (≥ 3 incidents)", level=1)
    if report["recurrent_nodes"]:
        for node in report["recurrent_nodes"]:
            doc.add_paragraph(
                f"{node['code']} {node['name']} : {node['total_incidents']} incidents",
                style="List Bullet",
            )
    else:
        doc.add_paragraph("Aucun nœud récurrent ce mois-ci.")

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
