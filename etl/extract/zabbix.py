"""
Zabbix collector — JSON-RPC `event.get` (cahier des charges §6.1).

Auth: either a static API token (ZABBIX_API_TOKEN, Zabbix ≥ 5.4) or
`user.login` with ZABBIX_USER/ZABBIX_PASSWORD (token valid ~30 min, so we
log in on every poll rather than caching it).
"""

import logging
from datetime import datetime, timezone

import requests

import config
from extract.common import match_node, skip_unmatched

logger = logging.getLogger(__name__)

# Zabbix trigger severities 0–5 → dashboard severities
SEVERITY_MAP = {0: "low", 1: "low", 2: "medium", 3: "medium", 4: "high", 5: "critical"}


def _rpc(method: str, params: dict, auth: str | None) -> dict:
    body = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    if auth:
        body["auth"] = auth
    r = requests.post(config.ZABBIX_API_URL, json=body, timeout=config.HTTP_TIMEOUT_S)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Zabbix API error: {data['error']}")
    return data["result"]


def _login() -> str:
    if config.ZABBIX_API_TOKEN:
        return config.ZABBIX_API_TOKEN
    return _rpc(
        "user.login",
        {"username": config.ZABBIX_USER, "password": config.ZABBIX_PASSWORD},
        auth=None,
    )


def fetch_events(nodes: list[dict], since: datetime) -> list[dict]:
    """New problem events since `since`, mapped onto dim_node codes."""
    token = _login()
    events = _rpc(
        "event.get",
        {
            "output": "extend",
            "time_from": int(since.timestamp()),
            "source": 0,  # trigger events
            "value": 1,  # PROBLEM (not recovery)
            "selectHosts": ["host", "name"],
            "sortfield": "clock",
            "sortorder": "ASC",
        },
        auth=token,
    )

    results = []
    for ev in events:
        hosts = ev.get("hosts") or [{}]
        host = hosts[0].get("host", "")
        node_code = match_node(nodes, host, hosts[0].get("name", ""))
        if node_code is None:
            skip_unmatched("zabbix", host)
            continue
        detected = datetime.fromtimestamp(int(ev["clock"]), tz=timezone.utc)
        results.append(
            {
                "node_code": node_code,
                "source_tool": "zabbix",
                "external_id": f"zabbix-event-{ev['eventid']}",
                "severity": SEVERITY_MAP.get(int(ev.get("severity", 0)), "medium"),
                "detected_at": detected.isoformat(),
                "description": ev.get("name") or "Alerte Zabbix",
                "cause_category": None,
                "cause_label": None,
            }
        )
    return results
