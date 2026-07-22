from __future__ import annotations

import hmac
from datetime import datetime, timezone

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import User
from .security import decode_access_token

settings = get_settings()


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_access_token(access_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid account")
    return user


def get_optional_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not access_token:
        return None
    try:
        payload = decode_access_token(access_token)
    except jwt.PyJWTError:
        return None
    user = db.get(User, payload["sub"])
    return user if user and user.is_active else None


def require_verified(user: User = Depends(get_current_user)) -> User:
    if not user.is_verified and settings.is_production:
        raise HTTPException(status_code=403, detail="Verify your email to continue")
    return user


def require_paid(user: User = Depends(require_verified)) -> User:
    if user.role == "admin":
        return user
    if user.tier not in {"pro", "elite"}:
        raise HTTPException(status_code=402, detail="A paid subscription is required")
    return user


def require_elite(user: User = Depends(require_verified)) -> User:
    if user.role == "admin":
        return user
    if user.tier != "elite":
        raise HTTPException(status_code=402, detail="Elite access is required")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user


def require_csrf(
    request: Request,
    csrf_cookie: str | None = Cookie(default=None, alias="csrf_token"),
    csrf_header: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    if not csrf_cookie or not csrf_header or not hmac.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def require_cron_secret(x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret")) -> None:
    if not x_cron_secret or not hmac.compare_digest(x_cron_secret, settings.cron_secret):
        raise HTTPException(status_code=401, detail="Invalid cron secret")


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
