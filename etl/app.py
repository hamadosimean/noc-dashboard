import logging
import os
import time

from load.api_client import NocApiClient
from pipelines.collector import run_forever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [etl] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_dsn() -> str:
    return (
        f"host={os.getenv('DB_HOST', 'postgres')} "
        f"port={os.getenv('DB_PORT', 5432)} "
        f"dbname={os.getenv('DB_NAME', 'noc_db')} "
        f"user={os.getenv('DB_USER', 'noc_db_user')} "
        f"password={os.getenv('DB_PASSWORD', '')}"
    )


def main() -> None:
    api_client = NocApiClient(
        base_url=os.getenv("NOC_API_URL", "http://backend:8000"),
        api_key=os.getenv("NOC_API_KEY", "dev-noc-api-key"),
    )

    logger.info("Waiting for NOC API to become healthy...")
    for _ in range(60):
        if api_client.is_healthy():
            break
        time.sleep(2)
    else:
        logger.warning("NOC API did not respond in time, starting the loop anyway")

    run_forever(build_dsn(), api_client)


if __name__ == "__main__":
    main()
