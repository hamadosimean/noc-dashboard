from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    node_code: str
    node_name: str
    locality: str
    severity: str
    status: str
    description: Optional[str] = None
    detected_at: datetime
    age_minutes: int
