from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.rate_limit import read_rate_limit
from app.core.security import get_current_user
from app.db.session import get_db
from app.services import cache_service, kpi_service

router = APIRouter(
    prefix="/api/sla",
    tags=["sla"],
    dependencies=[Depends(get_current_user), Depends(read_rate_limit)],
)


@router.get("")
def sla_status(month: int = Query(..., ge=1, le=12), year: int = Query(...), db: Session = Depends(get_db)):
    cache_key = f"kpi:sla:{year}:{month}"
    cached = cache_service.get_cached(cache_key)
    if cached is not None:
        return cached
    data = kpi_service.get_sla(db, month, year)
    cache_service.set_cached(cache_key, data)
    return data
