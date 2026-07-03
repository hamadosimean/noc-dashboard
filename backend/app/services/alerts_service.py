from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_open_alerts(db: Session, limit: int = 20) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT
              i.id, n.code AS node_code, n.name AS node_name, l.name AS locality,
              i.severity, i.status, i.description, i.detected_at
            FROM fact_incident i
            JOIN dim_node n ON i.node_id = n.id
            JOIN dim_locality l ON n.locality_id = l.id
            WHERE i.status IN ('open', 'acknowledged')
            ORDER BY i.detected_at ASC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings().all()

    now = datetime.now(timezone.utc)
    result = []
    for r in rows:
        detected_at = r["detected_at"]
        detected_at_aware = detected_at.replace(tzinfo=timezone.utc) if detected_at.tzinfo is None else detected_at
        age_minutes = int((now - detected_at_aware).total_seconds() // 60)
        result.append(
            {
                "id": r["id"],
                "node_code": r["node_code"],
                "node_name": r["node_name"],
                "locality": r["locality"],
                "severity": r["severity"],
                "status": r["status"],
                "description": r["description"],
                "detected_at": detected_at,
                "age_minutes": max(age_minutes, 0),
            }
        )
    return result
