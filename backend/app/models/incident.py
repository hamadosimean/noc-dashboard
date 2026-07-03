from sqlalchemy import BigInteger, Column, Computed, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Incident(Base):
    __tablename__ = "fact_incident"

    id = Column(BigInteger, primary_key=True)
    node_id = Column(Integer, ForeignKey("dim_node.id"), nullable=False)
    cause_id = Column(Integer, ForeignKey("dim_cause.id"))
    itop_ticket_id = Column(String(50))
    external_id = Column(String(100))
    status = Column(String(20), nullable=False, default="open")
    severity = Column(String(20), nullable=False, default="medium")
    detected_at = Column(DateTime, nullable=False)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    # Generated columns computed by PostgreSQL (see database/01_schema.sql) — never written by the ORM.
    mttr_minutes = Column(Integer, Computed("0"))
    downtime_minutes = Column(Integer, default=0)
    shift = Column(String(20), Computed("'auto'"))
    source_tool = Column(String(20), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    node = relationship("Node")
    cause = relationship("Cause")
