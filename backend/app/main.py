from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.constants import CACHE_TTL, CORS_ORIGINS
from app.routes import all_routers

app = FastAPI(title="NOC ANPTIC Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "NOC ANPTIC API is running", "cache_ttl": CACHE_TTL}
