import psycopg2


def load_active_nodes(dsn: str) -> list[tuple[str, str]]:
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT code, source_tool FROM dim_node WHERE is_active = TRUE")
            return cur.fetchall()
    finally:
        conn.close()
