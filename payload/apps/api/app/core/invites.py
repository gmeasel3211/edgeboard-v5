from __future__ import annotations

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import ALGORITHM
from app.models import SubscriptionTier

INVITE_ISSUER = "edgeboard-invite"


def create_invite_code(tier: SubscriptionTier, days_valid: int, label: str) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)
    payload = {
        "iss": INVITE_ISSUER,
        "purpose": "beta-access",
        "tier": tier.value,
        "label": label,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return f"EB-{token}", expires_at


def decode_invite_code(code: str | None) -> SubscriptionTier | None:
    if not code:
        return None
    normalized = code.strip()
    if normalized.startswith("EB-"):
        normalized = normalized[3:]
    try:
        payload = jwt.decode(normalized, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("iss") != INVITE_ISSUER or payload.get("purpose") != "beta-access":
            return None
        return SubscriptionTier(payload["tier"])
    except (JWTError, KeyError, ValueError):
        return None
