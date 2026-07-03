"""
Simulated collectors for Zabbix, Nagios, NetXMS and Centreon.

Cahier des charges §6 describes polling each tool's real API (Zabbix JSON-RPC
event.get, Nagios statusjson.cgi, Centreon webhook broker...). None of those
systems are reachable from this environment, so each function below fabricates
one plausible "new anomaly" event for a given node, in the shape that tool's
real collector would produce before normalization. Swap these for real HTTP
calls (see the docstrings) once the supervision tools are reachable.
"""
import random
from datetime import datetime, timezone

SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_WEIGHTS = [10, 25, 45, 20]

CAUSES_BY_TOOL = {
    "zabbix": [("Énergie", "Délestage / onduleur sans reprise auto"),
               ("Énergie", "Batterie onduleur déchargée"),
               ("Énergie", "Groupe électrogène en panne")],
    "nagios": [("Équipement", "Panne routeur"),
               ("Équipement", "Panne switch"),
               ("Liaison", "Latence réseau élevée")],
    "netxms": [("Équipement", "Surchauffe matérielle"),
               ("Liaison", "Coupure fibre optique")],
    "centreon": [("Liaison", "Perte de signal VSAT"),
                 ("Logiciel", "Service applicatif indisponible"),
                 ("Humain", "Intervention non planifiée")],
}


def _base_event(node_code: str, source_tool: str, external_prefix: str) -> dict:
    category, label = random.choice(CAUSES_BY_TOOL.get(source_tool, [("Logiciel", "Anomalie détectée")]))
    return {
        "node_code": node_code,
        "source_tool": source_tool,
        "external_id": f"{external_prefix}-{random.randint(100000, 999999)}",
        "severity": random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0],
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "cause_category": category,
        "cause_label": label,
        "description": label,
    }


def poll_zabbix(node_code: str) -> dict:
    """Real equivalent: POST event.get via JSON-RPC on /api_jsonrpc.php (§6.1)."""
    return _base_event(node_code, "zabbix", "zabbix-alert")


def poll_nagios(node_code: str) -> dict:
    """Real equivalent: GET /nagios/cgi-bin/statusjson.cgi?query=hostlist (§6.2)."""
    return _base_event(node_code, "nagios", "nagios-event")


def poll_netxms(node_code: str) -> dict:
    """Real equivalent: NetXMS REST API event query."""
    return _base_event(node_code, "netxms", "netxms-event")


def poll_centreon(node_code: str) -> dict:
    """Real equivalent: Centreon broker webhook payload (§6.3)."""
    return _base_event(node_code, "centreon", "centreon-event")


COLLECTORS = {
    "zabbix": poll_zabbix,
    "nagios": poll_nagios,
    "netxms": poll_netxms,
    "centreon": poll_centreon,
}


def simulate_event(node_code: str, source_tool: str) -> dict:
    collector = COLLECTORS.get(source_tool, poll_centreon)
    return collector(node_code)
