import json
import logging
from typing import Any, Optional

from app.core.constants import CACHE_TTL
from app.db.redis_client import redis_client

logger = logging.getLogger(__name__)


def get_cached(key: str) -> Optional[Any]:
    try:
        raw = redis_client.get(key)
    except Exception as exc:  # Redis unavailable should never break the API
        logger.warning("Redis GET failed for %s: %s", key, exc)
        return None
    return json.loads(raw) if raw else None


def set_cached(key: str, value: Any, ttl: int = CACHE_TTL) -> None:
    try:
        redis_client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as exc:
        logger.warning("Redis SET failed for %s: %s", key, exc)


def invalidate_prefix(prefix: str) -> None:
    try:
        for key in redis_client.scan_iter(match=f"{prefix}*"):
            redis_client.delete(key)
    except Exception as exc:
        logger.warning("Redis invalidation failed for prefix %s: %s", prefix, exc)
