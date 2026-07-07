import logging
import random

from celery_app import app
from config import NOC_API_KEY, NOC_API_URL, build_dsn
from extract.simulators import simulate_event
from load.api_client import NocApiClient
from pipelines.collector import load_active_nodes
from transform.normalize import to_ingest_payload

logger = logging.getLogger(__name__)

api_client = NocApiClient(base_url=NOC_API_URL, api_key=NOC_API_KEY)


@app.task(
    name="etl.collect_incident",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def collect_incident(self):
    """
    One collection tick: simulates one supervision-tool alert on a random active
    node and posts it to /api/incidents/ingest — approximating the always-on
    Zabbix/Nagios/Centreon -> webhook flow described in the cahier des charges
    Scheduled by Celery Beat (see celery_app.py).
    """
    nodes = load_active_nodes(build_dsn())
    if not nodes:
        logger.warning("No active nodes found, skipping this tick")
        return None

    node_code, source_tool = random.choice(nodes)
    event = simulate_event(node_code, source_tool)
    payload = to_ingest_payload(event)

    result = api_client.ingest_incident(payload)
    if result is None:
        raise self.retry(exc=RuntimeError(f"Ingest failed for {node_code}"))

    logger.info(
        "Ingested incident #%s on %s (ticket=%s)",
        result.get("incident_id"),
        node_code,
        result.get("itop_ticket_id"),
    )
    return result
