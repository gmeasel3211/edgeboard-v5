from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import SubscriptionTier, User

bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user_id = decode_access_token(credentials.credentials)
    user = db.get(User, user_id) if user_id else None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user


def admin_user(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user


def subscriber_user(
    user: User = Depends(current_user),
    x_edgeboard_view_as: str | None = Header(default=None),
) -> User:
    effective_tier = user.subscription_tier
    if user.is_admin and x_edgeboard_view_as in {"free", "pro", "elite"}:
        effective_tier = SubscriptionTier(x_edgeboard_view_as)

    if effective_tier == SubscriptionTier.FREE and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Paid subscription required")
    if user.is_admin and x_edgeboard_view_as == "free":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free-view simulation: this feature is locked on the Free plan",
        )
    return user
