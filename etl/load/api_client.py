import logging

import requests

logger = logging.getLogger(__name__)


class NocApiClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 5):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def is_healthy(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/", timeout=self.timeout)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def ingest_incident(self, payload: dict) -> dict | None:
        try:
            r = requests.post(
                f"{self.base_url}/api/incidents/ingest",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            logger.warning("Ingest failed for %s: %s", payload.get("node_code"), exc)
            return None
