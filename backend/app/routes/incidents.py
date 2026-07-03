from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, verify_api_key
from app.db.session import get_db
from app.models.user import User
from app.schemas.incidents import (
    AcknowledgePayload,
    IncidentIngestPayload,
    IncidentIngestResponse,
    ResolvePayload,
)
from app.services import cache_service, incident_service

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.post("/ingest", response_model=IncidentIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_incident(
    payload: IncidentIngestPayload,
    db: Session = Depends(get_db),
    _: None = Depends(verify_api_key),
):
    incident = incident_service.ingest_incident(db, payload)
    cache_service.invalidate_prefix("kpi:")
    return IncidentIngestResponse(
        incident_id=incident.id,
        node_id=incident.node_id,
        itop_ticket_id=incident.itop_ticket_id,
        shift=incident.shift,
        created_at=incident.created_at,
    )


@router.patch("/{incident_id}/resolve", response_model=IncidentIngestResponse)
def resolve_incident(
    incident_id: int,
    payload: ResolvePayload,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    incident = incident_service.resolve_incident(db, incident_id, payload.resolved_at, payload.notes)
    cache_service.invalidate_prefix("kpi:")
    return IncidentIngestResponse(
        incident_id=incident.id,
        node_id=incident.node_id,
        itop_ticket_id=incident.itop_ticket_id,
        shift=incident.shift,
        created_at=incident.created_at,
    )


@router.patch("/{incident_id}/acknowledge", response_model=IncidentIngestResponse)
def acknowledge_incident(
    incident_id: int,
    payload: AcknowledgePayload,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    incident = incident_service.acknowledge_incident(db, incident_id, payload.acknowledged_at)
    cache_service.invalidate_prefix("kpi:alerts")
    return IncidentIngestResponse(
        incident_id=incident.id,
        node_id=incident.node_id,
        itop_ticket_id=incident.itop_ticket_id,
        shift=incident.shift,
        created_at=incident.created_at,
    )
