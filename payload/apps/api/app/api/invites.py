from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import admin_user
from app.core.invites import create_invite_code
from app.models import User
from app.schemas import InviteCodeRequest, InviteCodeResponse

router = APIRouter(prefix="/admin/invites", tags=["Admin Invites"])


@router.post("", response_model=InviteCodeResponse)
def generate_invite(payload: InviteCodeRequest, _: User = Depends(admin_user)):
    code, expires_at = create_invite_code(payload.tier, payload.days_valid, payload.label)
    return InviteCodeResponse(
        code=code,
        tier=payload.tier,
        expires_at=expires_at,
        label=payload.label,
    )
