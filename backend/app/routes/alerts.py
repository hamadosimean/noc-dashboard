from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import alerts_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/open")
def open_alerts(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return alerts_service.get_open_alerts(db, limit)
