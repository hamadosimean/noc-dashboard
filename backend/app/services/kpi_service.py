from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

FRENCH_MONTHS = [
    "",
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]

CRITICAL_AVAILABILITY_THRESHOLD = 95.0
RECURRENT_MIN_COUNT_DEFAULT = 3


def month_label(month: int, year: int) -> str:
    return f"{FRENCH_MONTHS[month]} {year}"


def month_start(month: int, year: int) -> date:
    return date(year, month, 1)


def prev_month(month: int, year: int) -> tuple[int, int]:
    return (12, year - 1) if month == 1 else (month - 1, year)


def shift_months(month: int, year: int, offset: int) -> tuple[int, int]:
    total = (year * 12 + (month - 1)) - offset
    return (total % 12) + 1, total // 12


def get_summary(db: Session, month: int, year: int) -> dict:
    period_start = month_start(month, year)

    row = (
        db.execute(
            text("""
            SELECT
              COALESCE(SUM(total_incidents), 0)      AS total_incidents,
              COALESCE(SUM(resolved), 0)              AS resolved,
              COALESCE(AVG(avg_mttr), 0)               AS avg_mttr,
              COALESCE(AVG(availability_pct), 100)     AS availability_pct,
              COUNT(DISTINCT locality_id) FILTER (WHERE availability_pct < :threshold) AS critical_localities,
              COUNT(*) FILTER (WHERE total_incidents >= :min_count) AS recurrent_nodes
            FROM mv_kpi_node_monthly
            WHERE month = :period_start
            """),
            {
                "period_start": period_start,
                "threshold": CRITICAL_AVAILABILITY_THRESHOLD,
                "min_count": RECURRENT_MIN_COUNT_DEFAULT,
            },
        )
        .mappings()
        .first()
    )

    off_hours = db.execute(
        text("""
            SELECT COUNT(*) AS off_hours
            FROM fact_incident
            WHERE shift = 'auto'
              AND DATE_TRUNC('month', detected_at) = :period_start
            """),
        {"period_start": period_start},
    ).scalar()

    total_incidents = int(row["total_incidents"])
    resolved = int(row["resolved"])
    open_incidents = total_incidents - resolved
    resolution_rate = (
        round((resolved / total_incidents * 100), 1) if total_incidents else 0.0
    )

    pm_month, pm_year = prev_month(month, year)
    pm_period_start = month_start(pm_month, pm_year)
    prev_row = (
        db.execute(
            text("""
            SELECT
              COALESCE(SUM(total_incidents), 0)  AS total_incidents,
              COALESCE(AVG(availability_pct), 100) AS availability_pct
            FROM mv_kpi_node_monthly
            WHERE month = :period_start
            """),
            {"period_start": pm_period_start},
        )
        .mappings()
        .first()
    )

    kpi = {
        "total_incidents": total_incidents,
        "resolved": resolved,
        "open": open_incidents,
        "resolution_rate_pct": resolution_rate,
        "avg_mttr_minutes": round(float(row["avg_mttr"]), 1),
        "network_availability_pct": round(float(row["availability_pct"]), 1),
        "critical_localities": int(row["critical_localities"]),
        "recurrent_nodes": int(row["recurrent_nodes"]),
        "off_hours_detected": int(off_hours or 0),
    }

    vs_previous_month = {
        "incidents_delta": total_incidents - int(prev_row["total_incidents"]),
        "availability_delta": round(
            float(row["availability_pct"]) - float(prev_row["availability_pct"]), 1
        ),
    }

    return {
        "period": {"month": month, "year": year, "label": month_label(month, year)},
        "kpi": kpi,
        "vs_previous_month": vs_previous_month,
    }


def get_comparison(
    db: Session, month: int, year: int, offsets: tuple[int, ...] = (1, 3)
) -> dict:
    """Spec P2 « Comparaison périodes » — N vs N-1 and N vs N-3 months."""
    current = get_summary(db, month, year)
    comparisons = []
    for offset in offsets:
        m, y = shift_months(month, year, offset)
        past = get_summary(db, m, y)
        deltas = {
            key: round(current["kpi"][key] - past["kpi"][key], 1)
            for key in (
                "total_incidents",
                "resolved",
                "resolution_rate_pct",
                "avg_mttr_minutes",
                "network_availability_pct",
            )
        }
        comparisons.append(
            {
                "offset_months": offset,
                "period": past["period"],
                "kpi": past["kpi"],
                "deltas": deltas,
            }
        )
    return {"period": current["period"], "kpi": current["kpi"], "comparisons": comparisons}


def get_localities(db: Session, month: int, year: int, limit: int = 10) -> list[dict]:
    period_start = month_start(month, year)
    rows = (
        db.execute(
            text("""
            SELECT
              mv.locality_id,
              mv.locality,
              mv.region,
              l.latitude,
              l.longitude,
              SUM(mv.total_incidents)  AS total_incidents,
              SUM(mv.resolved)         AS resolved,
              AVG(mv.avg_mttr)         AS avg_mttr,
              AVG(mv.availability_pct) AS availability_pct
            FROM mv_kpi_node_monthly mv
            JOIN dim_locality l ON l.id = mv.locality_id
            WHERE mv.month = :period_start
            GROUP BY mv.locality_id, mv.locality, mv.region, l.latitude, l.longitude
            ORDER BY total_incidents DESC
            LIMIT :limit
            """),
            {"period_start": period_start, "limit": limit},
        )
        .mappings()
        .all()
    )

    return [
        {
            "locality_id": r["locality_id"],
            "locality": r["locality"],
            "region": r["region"],
            "latitude": float(r["latitude"]) if r["latitude"] is not None else None,
            "longitude": float(r["longitude"]) if r["longitude"] is not None else None,
            "total_incidents": int(r["total_incidents"]),
            "resolved": int(r["resolved"]),
            "avg_mttr": (
                round(float(r["avg_mttr"]), 1) if r["avg_mttr"] is not None else None
            ),
            "availability_pct": (
                round(float(r["availability_pct"]), 1)
                if r["availability_pct"] is not None
                else None
            ),
        }
        for r in rows
    ]


def get_localities_map(db: Session, month: int, year: int) -> list[dict]:
    """Every locality with a coordinate, for the map — including ones with zero
    incidents this month (unlike get_localities, which only returns localities
    that have activity in mv_kpi_node_monthly)."""
    period_start = month_start(month, year)
    rows = (
        db.execute(
            text("""
            SELECT
              l.id AS locality_id,
              l.name AS locality,
              r.name AS region,
              l.latitude,
              l.longitude,
              COALESCE(SUM(mv.total_incidents), 0)  AS total_incidents,
              COALESCE(SUM(mv.resolved), 0)         AS resolved,
              AVG(mv.avg_mttr)                       AS avg_mttr,
              COALESCE(AVG(mv.availability_pct), 100) AS availability_pct
            FROM dim_locality l
            JOIN dim_region r ON r.id = l.region_id
            LEFT JOIN mv_kpi_node_monthly mv
              ON mv.locality_id = l.id AND mv.month = :period_start
            WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
            GROUP BY l.id, l.name, r.name, l.latitude, l.longitude
            ORDER BY total_incidents DESC
            """),
            {"period_start": period_start},
        )
        .mappings()
        .all()
    )

    return [
        {
            "locality_id": r["locality_id"],
            "locality": r["locality"],
            "region": r["region"],
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "total_incidents": int(r["total_incidents"]),
            "resolved": int(r["resolved"]),
            "avg_mttr": (
                round(float(r["avg_mttr"]), 1) if r["avg_mttr"] is not None else None
            ),
            "availability_pct": round(float(r["availability_pct"]), 1),
        }
        for r in rows
    ]


def get_nodes(
    db: Session,
    month: int,
    year: int,
    locality_id: Optional[int] = None,
    limit: int = 10,
) -> list[dict]:
    period_start = month_start(month, year)
    rows = (
        db.execute(
            text("""
            SELECT node_id, code, name, source_tool, locality,
                   total_incidents, resolved, avg_mttr, availability_pct
            FROM mv_kpi_node_monthly
            WHERE month = :period_start
              AND (:locality_id IS NULL OR locality_id = :locality_id)
            ORDER BY total_incidents DESC
            LIMIT :limit
            """),
            {"period_start": period_start, "locality_id": locality_id, "limit": limit},
        )
        .mappings()
        .all()
    )

    return [
        {
            "node_id": r["node_id"],
            "code": r["code"],
            "name": r["name"],
            "locality": r["locality"],
            "source_tool": r["source_tool"],
            "total_incidents": int(r["total_incidents"]),
            "resolved": int(r["resolved"]),
            "avg_mttr": (
                round(float(r["avg_mttr"]), 1) if r["avg_mttr"] is not None else None
            ),
            "availability_pct": (
                round(float(r["availability_pct"]), 1)
                if r["availability_pct"] is not None
                else None
            ),
        }
        for r in rows
    ]


def get_recurrent_nodes(
    db: Session, month: int, year: int, min_count: int = 3
) -> list[dict]:
    period_start = month_start(month, year)
    rows = (
        db.execute(
            text("""
            SELECT node_id, code, name, locality, total_incidents
            FROM mv_kpi_node_monthly
            WHERE month = :period_start AND total_incidents >= :min_count
            ORDER BY total_incidents DESC
            """),
            {"period_start": period_start, "min_count": min_count},
        )
        .mappings()
        .all()
    )

    return [
        {
            "node_id": r["node_id"],
            "code": r["code"],
            "name": r["name"],
            "locality": r["locality"],
            "total_incidents": int(r["total_incidents"]),
        }
        for r in rows
    ]


def get_trend(db: Session, month: int, year: int, months: int = 6) -> list[dict]:
    points = []
    for offset in range(months - 1, -1, -1):
        m, y = shift_months(month, year, offset)
        period_start = month_start(m, y)
        row = (
            db.execute(
                text("""
                SELECT
                  COALESCE(SUM(total_incidents), 0) AS total_incidents,
                  COALESCE(SUM(resolved), 0)         AS resolved,
                  COALESCE(AVG(avg_mttr), 0)          AS avg_mttr,
                  COALESCE(AVG(availability_pct), 100) AS availability_pct
                FROM mv_kpi_node_monthly
                WHERE month = :period_start
                """),
                {"period_start": period_start},
            )
            .mappings()
            .first()
        )
        points.append(
            {
                "month": m,
                "year": y,
                "label": month_label(m, y),
                "total_incidents": int(row["total_incidents"]),
                "resolved": int(row["resolved"]),
                "avg_mttr": round(float(row["avg_mttr"]), 1),
                "availability_pct": round(float(row["availability_pct"]), 1),
            }
        )
    return points


def get_hour_distribution(db: Session, month: int, year: int) -> list[dict]:
    period_start = month_start(month, year)
    rows = (
        db.execute(
            text("""
            SELECT EXTRACT(HOUR FROM detected_at)::int AS hour, COUNT(*) AS total_incidents
            FROM fact_incident
            WHERE DATE_TRUNC('month', detected_at) = :period_start
            GROUP BY hour
            """),
            {"period_start": period_start},
        )
        .mappings()
        .all()
    )

    counts = {int(r["hour"]): int(r["total_incidents"]) for r in rows}
    return [{"hour": h, "total_incidents": counts.get(h, 0)} for h in range(24)]


def get_latest_data_month(db: Session) -> tuple[int, int]:
    row = (
        db.execute(text("SELECT MAX(month) AS latest FROM mv_kpi_node_monthly"))
        .mappings()
        .first()
    )
    latest = row["latest"]
    if latest is None:
        today = date.today()
        return today.month, today.year
    return latest.month, latest.year


def get_cause_breakdown(db: Session, month: int, year: int) -> list[dict]:
    period_start = month_start(month, year)
    rows = (
        db.execute(
            text("""
            SELECT c.category, COUNT(i.id) AS total_incidents, AVG(i.mttr_minutes) AS avg_mttr
            FROM fact_incident i
            JOIN dim_cause c ON i.cause_id = c.id
            WHERE DATE_TRUNC('month', i.detected_at) = :period_start
            GROUP BY c.category
            ORDER BY total_incidents DESC
            """),
            {"period_start": period_start},
        )
        .mappings()
        .all()
    )

    return [
        {
            "category": r["category"],
            "total_incidents": int(r["total_incidents"]),
            "avg_mttr": (
                round(float(r["avg_mttr"]), 1) if r["avg_mttr"] is not None else None
            ),
        }
        for r in rows
    ]


SLA_TARGETS = {
    "core_availability": ("Disponibilité Cœur de Réseau", 99.5),
    "node_availability": ("Disponibilité Nœuds d'Accès", 95.0),
    "resolution_rate": ("Taux de Résolution < 4h", 80.0),
}


def get_sla(db: Session, month: int, year: int) -> dict:
    summary = get_summary(db, month, year)
    kpi = summary["kpi"]

    period_start = month_start(month, year)
    core_row = (
        db.execute(
            text("""
            SELECT AVG(availability_pct) AS availability_pct
            FROM mv_kpi_node_monthly
            WHERE month = :period_start AND source_tool IN ('centreon', 'netxms')
            """),
            {"period_start": period_start},
        )
        .mappings()
        .first()
    )
    core_availability = (
        round(float(core_row["availability_pct"]), 1)
        if core_row and core_row["availability_pct"] is not None
        else kpi["network_availability_pct"]
    )

    values = {
        "core_availability": core_availability,
        "node_availability": kpi["network_availability_pct"],
        "resolution_rate": kpi["resolution_rate_pct"],
    }

    indicators = []
    for key, (label, target) in SLA_TARGETS.items():
        value = values[key]
        indicators.append(
            {
                "metric": label,
                "value": value,
                "target": target,
                "status": "met" if value >= target else "not_met",
            }
        )

    return {
        "period": summary["period"],
        "indicators": indicators,
    }


def get_locality_nodes(
    db: Session, locality_id: int, month: int, year: int
) -> Optional[dict]:
    period_start = month_start(month, year)

    locality_row = (
        db.execute(
            text("""
            SELECT l.id AS locality_id, l.name AS locality, r.name AS region
            FROM dim_locality l
            JOIN dim_region r ON l.region_id = r.id
            WHERE l.id = :locality_id
            """),
            {"locality_id": locality_id},
        )
        .mappings()
        .first()
    )
    if locality_row is None:
        return None

    rows = (
        db.execute(
            text("""
            SELECT
              n.id AS node_id, n.code, n.name, n.node_type, n.source_tool, n.is_active,
              COALESCE(mv.total_incidents, 0) AS total_incidents,
              COALESCE(mv.resolved, 0)        AS resolved,
              mv.avg_mttr,
              COALESCE(mv.availability_pct, 100) AS availability_pct
            FROM dim_node n
            LEFT JOIN mv_kpi_node_monthly mv
              ON mv.node_id = n.id AND mv.month = :period_start
            WHERE n.locality_id = :locality_id
            ORDER BY total_incidents DESC, n.code
            """),
            {"locality_id": locality_id, "period_start": period_start},
        )
        .mappings()
        .all()
    )

    nodes = [
        {
            "node_id": r["node_id"],
            "code": r["code"],
            "name": r["name"],
            "node_type": r["node_type"],
            "source_tool": r["source_tool"],
            "is_active": r["is_active"],
            "total_incidents": int(r["total_incidents"]),
            "resolved": int(r["resolved"]),
            "open": int(r["total_incidents"]) - int(r["resolved"]),
            "avg_mttr": (
                round(float(r["avg_mttr"]), 1) if r["avg_mttr"] is not None else None
            ),
            "availability_pct": round(float(r["availability_pct"]), 1),
        }
        for r in rows
    ]

    return {
        "locality_id": locality_row["locality_id"],
        "locality": locality_row["locality"],
        "region": locality_row["region"],
        "period": {"month": month, "year": year, "label": month_label(month, year)},
        "nodes": nodes,
    }
