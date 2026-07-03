from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import NOC_API_KEY
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import decode_access_token


def verify_api_key(authorization: str = Header(default="")) -> None:
    """Static bearer key required on supervision-tool webhooks (Centreon/Zabbix -> /ingest).

    Matches the cahier des charges §10.1: "clé API statique pour les webhooks".
    """
    expected = f"Bearer {NOC_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    """JWT-bearer auth for dashboard-driven actions (e.g. acknowledge/resolve)."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
