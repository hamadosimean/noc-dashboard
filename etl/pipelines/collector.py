import logging
import random
import time

import psycopg2

from extract.simulators import simulate_event
from load.api_client import NocApiClient
from transform.normalize import to_ingest_payload

logger = logging.getLogger(__name__)


def load_active_nodes(dsn: str) -> list[tuple[str, str]]:
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT code, source_tool FROM dim_node WHERE is_active = TRUE")
            return cur.fetchall()
    finally:
        conn.close()


def run_forever(
    dsn: str,
    api_client: NocApiClient,
    min_interval_s: int = 20,
    max_interval_s: int = 60,
) -> None:
    """
    Periodically simulates one supervision-tool alert on a random active node and
    posts it to /api/incidents/ingest — approximating the always-on Zabbix/Nagios/
    Centreon -> webhook flow described in the cahier des charges (§2.2, §7.1).
    """
    nodes = load_active_nodes(dsn)
    logger.info("Loaded %d active nodes for incident simulation", len(nodes))

    while True:
        time.sleep(random.randint(min_interval_s, max_interval_s))
        if not nodes:
            nodes = load_active_nodes(dsn)
            if not nodes:
                continue

        node_code, source_tool = random.choice(nodes)
        event = simulate_event(node_code, source_tool)
        payload = to_ingest_payload(event)
        result = api_client.ingest_incident(payload)
        if result:
            logger.info(
                "Ingested incident #%s on %s (ticket=%s)",
                result.get("incident_id"), node_code, result.get("itop_ticket_id"),
            )
