from typing import List, Optional

from pydantic import BaseModel


class Period(BaseModel):
    month: int
    year: int
    label: str


class KPISummaryValues(BaseModel):
    total_incidents: int
    resolved: int
    open: int
    resolution_rate_pct: float
    avg_mttr_minutes: float
    network_availability_pct: float
    critical_localities: int
    recurrent_nodes: int
    off_hours_detected: int


class KPISummaryDelta(BaseModel):
    incidents_delta: int
    availability_delta: float


class KPISummaryResponse(BaseModel):
    period: Period
    kpi: KPISummaryValues
    vs_previous_month: KPISummaryDelta


class LocalityKPIOut(BaseModel):
    locality_id: int
    locality: str
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_incidents: int
    resolved: int
    avg_mttr: Optional[float] = None
    availability_pct: Optional[float] = None


class NodeKPIOut(BaseModel):
    node_id: int
    code: str
    name: str
    locality: str
    source_tool: str
    total_incidents: int
    resolved: int
    avg_mttr: Optional[float] = None
    availability_pct: Optional[float] = None


class RecurrentNodeOut(BaseModel):
    node_id: int
    code: str
    name: str
    locality: str
    total_incidents: int


class TrendPointOut(BaseModel):
    month: int
    year: int
    label: str
    total_incidents: int
    resolved: int
    avg_mttr: Optional[float] = None
    availability_pct: Optional[float] = None


class HourDistributionOut(BaseModel):
    hour: int
    total_incidents: int


class NodeDetailOut(BaseModel):
    node_id: int
    code: str
    name: str
    node_type: str
    source_tool: str
    is_active: bool
    total_incidents: int
    resolved: int
    open: int
    avg_mttr: Optional[float] = None
    availability_pct: Optional[float] = None


class LocalityNodesResponse(BaseModel):
    locality_id: int
    locality: str
    region: str
    period: Period
    nodes: List[NodeDetailOut]
