from fastapi import FastAPI
from app.core.constants import CACHE_TTL

app = FastAPI(title="NOC ANPTIC Dashboard API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "NOC ANPTIC API is running", "cache_ttl": CACHE_TTL}

@app.get("/api/kpi/summary")
def get_kpi_summary(month: int, year: int):
    return {
        "period": {"month": month, "year": year, "label": f"{month}/{year}"},
        "kpi": {
            "total_incidents": 32,
            "resolved": 21,
            "open": 11,
            "resolution_rate_pct": 65.6,
            "avg_mttr_minutes": 138,
            "network_availability_pct": 93.8,
            "critical_localities": 3,
            "recurrent_nodes": 7,
            "off_hours_detected": 7
        }
    }
