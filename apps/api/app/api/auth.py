from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..dependencies import client_ip, get_current_user, require_csrf
from ..models import OneTimeToken, RefreshToken, User
from ..schemas import (
    AuthResponse,
    LoginRequest,
    Message,
    PasswordRequest,
    PasswordReset,
    UserCreate,
    UserOut,
    VerifyEmail,
)
from ..security import (
    create_access_token,
    create_csrf_token,
    create_one_time_token,
    create_refresh_token,
    hash_one_time_token,
    hash_password,
    hash_refresh_token,
    normalize_email,
    verify_password,
)
from ..services.email import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookies(response: Response, user: User, refresh_raw: str, csrf_token: str) -> None:
    common = {
        "secure": settings.cookie_secure,
        "samesite": settings.cookie_samesite,
        "domain": settings.cookie_domain,
        "path": "/",
    }
    response.set_cookie(
        "access_token",
        create_access_token(user.id, user.role, user.tier),
        httponly=True,
        max_age=settings.access_token_minutes * 60,
        **common,
    )
    response.set_cookie(
        "refresh_token",
        refresh_raw,
        httponly=True,
        max_age=settings.refresh_token_days * 86400,
        **common,
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,
        max_age=settings.refresh_token_days * 86400,
        **common,
    )


def _clear_auth_cookies(response: Response) -> None:
    for key in ("access_token", "refresh_token", "csrf_token"):
        response.delete_cookie(key, domain=settings.cookie_domain, path="/")


def _new_refresh_record(db: Session, user: User, raw: str, request: Request) -> RefreshToken:
    record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    db.add(record)
    return record


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    payload: UserCreate,
    request: Request,
    response: Response,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
) -> AuthResponse:
    email = normalize_email(payload.email)
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    user = User(email=email, display_name=payload.display_name.strip(), password_hash=password_hash)
    db.add(user)
    db.flush()
    raw_verify, verify_hash = create_one_time_token()
    db.add(
        OneTimeToken(
            user_id=user.id,
            purpose="verify_email",
            token_hash=verify_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
    )
    refresh_raw = create_refresh_token()
    _new_refresh_record(db, user, refresh_raw, request)
    db.commit()
    csrf = create_csrf_token()
    _set_auth_cookies(response, user, refresh_raw, csrf)
    background.add_task(send_verification_email, user.email, raw_verify)
    return AuthResponse(user=UserOut.model_validate(user), csrf_token=csrf)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == normalize_email(payload.email)))
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    user.last_login_at = datetime.now(timezone.utc)
    refresh_raw = create_refresh_token()
    _new_refresh_record(db, user, refresh_raw, request)
    db.commit()
    csrf = create_csrf_token()
    _set_auth_cookies(response, user, refresh_raw, csrf)
    return AuthResponse(user=UserOut.model_validate(user), csrf_token=csrf)


@router.post("/refresh", response_model=AuthResponse)
def refresh_session(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> AuthResponse:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    token_hash = hash_refresh_token(refresh_token)
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    now = datetime.now(timezone.utc)
    expires_at = record.expires_at if record else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not record or record.revoked_at or not expires_at or expires_at <= now:
        _clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Session expired")
    user = db.get(User, record.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid account")
    replacement_raw = create_refresh_token()
    replacement = _new_refresh_record(db, user, replacement_raw, request)
    db.flush()
    record.revoked_at = now
    record.replaced_by_hash = replacement.token_hash
    db.commit()
    csrf = create_csrf_token()
    _set_auth_cookies(response, user, replacement_raw, csrf)
    return AuthResponse(user=UserOut.model_validate(user), csrf_token=csrf)


@router.post("/logout", response_model=Message, dependencies=[Depends(require_csrf)])
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> Message:
    if refresh_token:
        record = db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(refresh_token))
        )
        if record and not record.revoked_at:
            record.revoked_at = datetime.now(timezone.utc)
            db.commit()
    _clear_auth_cookies(response)
    return Message(message="Logged out")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/verify-email", response_model=Message)
def verify_email(payload: VerifyEmail, db: Session = Depends(get_db)) -> Message:
    token_hash = hash_one_time_token(payload.token)
    record = db.scalar(
        select(OneTimeToken).where(
            OneTimeToken.token_hash == token_hash,
            OneTimeToken.purpose == "verify_email",
        )
    )
    now = datetime.now(timezone.utc)
    expires_at = record.expires_at if record else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not record or record.used_at or not expires_at or expires_at <= now:
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired")
    user = db.get(User, record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    user.is_verified = True
    record.used_at = now
    db.commit()
    return Message(message="Email verified")


@router.post("/request-password-reset", response_model=Message)
async def request_password_reset(
    payload: PasswordRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Message:
    user = db.scalar(select(User).where(User.email == normalize_email(payload.email)))
    if user:
        raw, hashed = create_one_time_token()
        db.add(
            OneTimeToken(
                user_id=user.id,
                purpose="password_reset",
                token_hash=hashed,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        )
        db.commit()
        background.add_task(send_password_reset_email, user.email, raw)
    return Message(message="If the account exists, a reset link has been sent")


@router.post("/reset-password", response_model=Message)
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)) -> Message:
    token_hash = hash_one_time_token(payload.token)
    record = db.scalar(
        select(OneTimeToken).where(
            OneTimeToken.token_hash == token_hash,
            OneTimeToken.purpose == "password_reset",
        )
    )
    now = datetime.now(timezone.utc)
    expires_at = record.expires_at if record else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not record or record.used_at or not expires_at or expires_at <= now:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    user = db.get(User, record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        user.password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    record.used_at = now
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)).update(
        {RefreshToken.revoked_at: now}
    )
    db.commit()
    return Message(message="Password updated")
