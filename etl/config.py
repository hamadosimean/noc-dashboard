import os


def build_dsn() -> str:
    return (
        f"host={os.getenv('DB_HOST', 'postgres')} "
        f"port={os.getenv('DB_PORT', 5432)} "
        f"dbname={os.getenv('DB_NAME', 'noc_db')} "
        f"user={os.getenv('DB_USER', 'noc_db_user')} "
        f"password={os.getenv('DB_PASSWORD', '')}"
    )


def broker_url() -> str:
    host = os.getenv("REDIS_HOST", "redis")
    port = os.getenv("REDIS_PORT", "6379")
    # DB 1: the backend cache uses the default DB 0 on the same Redis instance.
    db = os.getenv("CELERY_BROKER_DB", "1")
    return f"redis://{host}:{port}/{db}"


NOC_API_URL = os.getenv("NOC_API_URL", "http://backend:8000")
NOC_API_KEY = os.getenv("NOC_API_KEY", "dev-noc-api-key")
COLLECT_INTERVAL_S = int(os.getenv("ETL_COLLECT_INTERVAL_S", "30"))
# Where the scheduled end-of-month exports are written (mounted volume).
REPORTS_DIR = os.getenv("REPORTS_DIR", "/reports")
