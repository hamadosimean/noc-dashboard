from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.session import Base


class KpiNodeMonthly(Base):
    """Read-only mapping of the mv_kpi_node_monthly materialized view
    (see database/01_schema.sql). One row per (month, node) with the
    pre-aggregated monthly KPIs; never written through the ORM — it's
    maintained by REFRESH MATERIALIZED VIEW (nightly ETL job, plus
    per-write refresh when SYNC_MV_REFRESH=true)."""

    __tablename__ = "mv_kpi_node_monthly"

    month = Column(DateTime, primary_key=True)
    node_id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(200))
    source_tool = Column(String(20))
    locality_id = Column(Integer)
    locality = Column(String(150))
    region = Column(String(100))
    total_incidents = Column(Integer)
    resolved = Column(Integer)
    avg_mttr = Column(Float)
    total_downtime = Column(Integer)
    availability_pct = Column(Float)
