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


def get_current_user(
    authorization: str = Header(default=""), db: Session = Depends(get_db)
) -> User:
    """JWT-bearer auth for dashboard-driven actions (e.g. acknowledge/resolve)."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_role(*roles: str):
    """RBAC per spec §10.1 — admin (read+write), analyst (read-only),
    noc_agent (read + acknowledge)."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.role}' is not allowed for this action",
            )
        return current_user

    return dependency


def verify_user_or_api_key(
    authorization: str = Header(default=""), db: Session = Depends(get_db)
) -> None:
    """Accept either a dashboard JWT or the static NOC API key.

    Used on /api/report/monthly so the scheduled ETL export (which only holds
    the webhook API key) can pull the end-of-month report."""
    if authorization == f"Bearer {NOC_API_KEY}":
        return
    get_current_user(authorization, db)
