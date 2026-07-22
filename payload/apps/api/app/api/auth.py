from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.invites import decode_invite_code
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


def sync_admin_status(user: User, db: Session) -> None:
    should_be_admin = user.email.lower() == settings.admin_email.lower()
    if user.is_admin != should_be_admin:
        user.is_admin = should_be_admin
        db.add(user)
        db.commit()
        db.refresh(user)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    invited_tier = decode_invite_code(payload.invite_code)
    if payload.invite_code and invited_tier is None:
        raise HTTPException(status_code=400, detail="That invite code is invalid or expired")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
        is_admin=email == settings.admin_email.lower(),
        subscription_tier=invited_tier or "free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    sync_admin_status(user, db)
    return AuthResponse(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    sync_admin_status(user, db)
    return user
