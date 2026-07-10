import psycopg2


def load_active_nodes(dsn: str) -> list[dict]:
    """Active nodes with everything the collectors need to map a
    supervision-tool host reference back onto a dim_node code."""
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code, name, host(ip_address), source_tool"
                " FROM dim_node WHERE is_active = TRUE"
            )
            return [
                {"code": code, "name": name, "ip_address": ip, "source_tool": tool}
                for code, name, ip, tool in cur.fetchall()
            ]
    finally:
        conn.close()
