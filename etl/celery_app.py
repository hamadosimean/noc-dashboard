import logging
import os

from celery import Celery
from celery.schedules import crontab

from config import COLLECT_INTERVAL_S, broker_url

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [etl] %(levelname)s %(message)s",
)

app = Celery("etl", broker=broker_url(), include=["pipelines.tasks"])

app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_ignore_result=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    # Drop a collection tick instead of piling them up if the API is down.
    task_time_limit=60,
    beat_schedule={
        "collect-supervision-events": {
            "task": "etl.collect_incident",
            "schedule": float(COLLECT_INTERVAL_S),
            "options": {"expires": COLLECT_INTERVAL_S},
        },
        # Spec §2.2 — nightly recompute of the monthly KPI materialized view.
        "refresh-kpi-view-nightly": {
            "task": "etl.refresh_kpi_view",
            "schedule": crontab(hour=2, minute=0),
        },
        # Spec §1.2 (P1) — automatic end-of-month report, archived after the refresh.
        "generate-monthly-report": {
            "task": "etl.generate_monthly_report",
            "schedule": crontab(day_of_month=1, hour=2, minute=30),
        },
    },
)
