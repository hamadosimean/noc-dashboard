"""
Redis pub/sub bridge between incident ingestion and the /ws/alerts WebSocket.

The HTTP worker publishes each new incident on ALERT_CHANNEL; every open
WebSocket connection (possibly on another uvicorn worker) is subscribed and
forwards the message to its client.
"""
import json
import logging
from typing import Any

from app.db.redis_client import redis_client

logger = logging.getLogger(__name__)

ALERT_CHANNEL = "noc:alerts"


def publish_alert(event: dict[str, Any]) -> None:
    try:
        redis_client.publish(ALERT_CHANNEL, json.dumps(event, default=str))
    except Exception as exc:  # a broken broadcast must not break ingestion
        logger.warning("Alert broadcast failed: %s", exc)
