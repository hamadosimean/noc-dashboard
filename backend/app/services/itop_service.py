"""
Stub iTop CMDB/ITSM client.

The real integration (see cahier des charges §6.4) posts to iTop's REST webservice
(core/create on class Incident) using ITOP_URL/ITOP_USER/ITOP_PASS. No live iTop
instance is reachable from this environment, so ticket creation is simulated here:
it deterministically mints a "TKT-<year>-<incident_id>" reference, which is exactly
the shape the real endpoint returns. Swap the body of create_ticket() for a real
`requests.post(ITOP_URL, ...)` call once iTop credentials are available.
"""
from datetime import datetime, timezone


def create_ticket(incident_id: int, node_code: str, description: str | None) -> str:
    year = datetime.now(timezone.utc).year
    return f"TKT-{year}-{incident_id:05d}"
