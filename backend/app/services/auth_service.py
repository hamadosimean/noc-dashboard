import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, JWT_SECRET
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def hash_pin(pin: str) -> str:
    # Fast, deterministic hash so a quick-login PIN can be looked up directly
    # (a short numeric PIN doesn't warrant adaptive/salted hashing — see §10.1
    # and the note on dim_user.pin_hash in database/01_schema.sql).
    return hashlib.sha256(pin.encode()).hexdigest()


def create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": expires_at,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def authenticate_with_password(db: Session, username: str, password: str) -> User:
    user = (
        db.query(User)
        .filter(User.username == username, User.is_active.is_(True))
        .first()
    )
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    _touch_last_login(db, user)
    return user


def authenticate_with_pin(db: Session, pin: str) -> User:
    user = (
        db.query(User)
        .filter(User.pin_hash == hash_pin(pin), User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Code PIN invalide")
    _touch_last_login(db, user)
    return user


def _touch_last_login(db: Session, user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
