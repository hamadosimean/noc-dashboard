"""
NetXMS collector — REST API alarm query (cahier des charges §6, "NetXMS API").

Targets the NetXMS web API daemon (nxweb / netxms-websvc): GET {url}/alarms
with Basic auth. Active alarms are polled, so an alarm that stays active keeps
its (stable) alarm id — the backend deduplicates open incidents on
(source_tool, external_id).
"""

import logging
from datetime import datetime, timezone

import requests

import config
from extract.common import match_node, skip_unmatched

logger = logging.getLogger(__name__)

# NetXMS severities 0–4: NORMAL, WARNING, MINOR, MAJOR, CRITICAL
SEVERITY_MAP = {0: "low", 1: "medium", 2: "medium", 3: "high", 4: "critical"}


def fetch_events(nodes: list[dict], since: datetime) -> list[dict]:
    url = f"{config.NETXMS_API_URL.rstrip('/')}/alarms"
    r = requests.get(
        url,
        auth=(config.NETXMS_USER, config.NETXMS_PASSWORD),
        timeout=config.HTTP_TIMEOUT_S,
    )
    r.raise_for_status()
    payload = r.json()
    alarms = payload.get("alarms", payload if isinstance(payload, list) else [])

    results = []
    for alarm in alarms:
        severity_raw = int(alarm.get("currentSeverity", alarm.get("severity", 1)))
        if severity_raw == 0:  # NORMAL — not an incident
            continue
        host = str(
            alarm.get("sourceObjectName")
            or alarm.get("objectName")
            or alarm.get("sourceObjectId", "")
        )
        node_code = match_node(nodes, host)
        if node_code is None:
            skip_unmatched("netxms", host)
            continue
        created_raw = alarm.get("creationTime") or alarm.get("creationTimestamp")
        if created_raw is not None:
            detected = datetime.fromtimestamp(int(created_raw), tz=timezone.utc)
        else:
            detected = datetime.now(timezone.utc)
        results.append(
            {
                "node_code": node_code,
                "source_tool": "netxms",
                "external_id": f"netxms-alarm-{alarm.get('id')}",
                "severity": SEVERITY_MAP.get(severity_raw, "medium"),
                "detected_at": detected.isoformat(),
                "description": alarm.get("message") or "Alarme NetXMS",
                "cause_category": None,
                "cause_label": None,
            }
        )
    return results
