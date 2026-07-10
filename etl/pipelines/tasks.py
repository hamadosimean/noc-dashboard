import logging
import os
import random
from datetime import date, timedelta

import psycopg2

from celery_app import app
from config import NOC_API_KEY, NOC_API_URL, REPORTS_DIR, build_dsn
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


@app.task(name="etl.refresh_kpi_view", bind=True, max_retries=2, default_retry_delay=60)
def refresh_kpi_view(self):
    """
    Nightly 02:00 batch (spec §2.2): recompute the monthly KPI materialized view.
    CONCURRENTLY so dashboard reads are never blocked (the view has the unique
    index on (month, node_id) that CONCURRENTLY requires).
    """
    try:
        conn = psycopg2.connect(build_dsn())
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_kpi_node_monthly")
        conn.close()
        logger.info("mv_kpi_node_monthly refreshed")
    except psycopg2.Error as exc:
        raise self.retry(exc=exc)


@app.task(name="etl.generate_monthly_report", bind=True, max_retries=3, default_retry_delay=300)
def generate_monthly_report(self):
    """
    End-of-month automatic export (spec §1.2 « Rapport mensuel », P1).
    Runs on the 1st at 02:30, right after the nightly KPI refresh, and archives
    the previous month's report in PDF and DOCX under REPORTS_DIR.
    """
    last_month = date.today().replace(day=1) - timedelta(days=1)
    month, year = last_month.month, last_month.year

    os.makedirs(REPORTS_DIR, exist_ok=True)
    written = []
    for fmt in ("pdf", "docx"):
        content = api_client.download_monthly_report(month, year, fmt)
        if content is None:
            raise self.retry(exc=RuntimeError(f"Report {fmt} download failed"))
        path = os.path.join(REPORTS_DIR, f"rapport-noc-{year}-{month:02d}.{fmt}")
        with open(path, "wb") as fh:
            fh.write(content)
        written.append(path)

    logger.info("Monthly report archived: %s", ", ".join(written))
    return written
