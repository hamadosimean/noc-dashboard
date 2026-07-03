from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Region(Base):
    __tablename__ = "dim_region"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    localities = relationship("Locality", back_populates="region")


class Locality(Base):
    __tablename__ = "dim_locality"

    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("dim_region.id"), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    population = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    region = relationship("Region", back_populates="localities")
    nodes = relationship("Node", back_populates="locality")


class Node(Base):
    __tablename__ = "dim_node"

    id = Column(Integer, primary_key=True)
    locality_id = Column(Integer, ForeignKey("dim_locality.id"), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    node_type = Column(String(50), nullable=False)
    ip_address = Column(String(50))
    source_tool = Column(String(20), nullable=False)
    itop_ci_id = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    locality = relationship("Locality", back_populates="nodes")


class Cause(Base):
    __tablename__ = "dim_cause"

    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)
    label = Column(String(150), nullable=False)
