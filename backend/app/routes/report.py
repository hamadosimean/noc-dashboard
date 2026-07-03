from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import report_service

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/monthly")
def monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    format: str = Query("json", pattern="^(json|pdf)$"),
    db: Session = Depends(get_db),
):
    data = report_service.build_report_data(db, month, year)
    if format == "json":
        return data

    pdf_bytes = report_service.render_pdf(data)
    filename = f"rapport-noc-{year}-{month:02d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
