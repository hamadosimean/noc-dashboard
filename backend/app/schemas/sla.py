from typing import List

from pydantic import BaseModel

from app.schemas.kpi import Period


class SLAIndicatorOut(BaseModel):
    metric: str
    value: float
    target: float
    status: str  # "met" | "not_met"


class SLAResponse(BaseModel):
    period: Period
    indicators: List[SLAIndicatorOut]
