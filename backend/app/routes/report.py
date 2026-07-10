from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.rate_limit import read_rate_limit
from app.core.security import verify_user_or_api_key
from app.db.session import get_db
from app.services import report_service

# Accepts a dashboard JWT or the static API key (used by the scheduled
# end-of-month export running in the ETL beat container).
router = APIRouter(
    prefix="/api/report",
    tags=["report"],
    dependencies=[Depends(verify_user_or_api_key), Depends(read_rate_limit)],
)

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.get("/monthly")
def monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    format: str = Query("json", pattern="^(json|pdf|docx)$"),
    db: Session = Depends(get_db),
):
    data = report_service.build_report_data(db, month, year)
    if format == "json":
        return data

    if format == "pdf":
        content = report_service.render_pdf(data)
    else:
        content = report_service.render_docx(data)
    filename = f"rapport-noc-{year}-{month:02d}.{format}"
    return Response(
        content=content,
        media_type=MEDIA_TYPES[format],
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
