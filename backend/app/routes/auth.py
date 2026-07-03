from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginPayload, PinLoginPayload, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = auth_service.authenticate_with_password(db, payload.username, payload.password)
    return TokenResponse(access_token=auth_service.create_access_token(user), user=UserOut.model_validate(user))


@router.post("/pin-login", response_model=TokenResponse)
def pin_login(payload: PinLoginPayload, db: Session = Depends(get_db)):
    user = auth_service.authenticate_with_pin(db, payload.pin)
    return TokenResponse(access_token=auth_service.create_access_token(user), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
