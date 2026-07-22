from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import require_admin, require_csrf
from ..models import AuditLog, User
from ..schemas import Message, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def account(user: User = Depends(require_admin)) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/{user_id}/disable", response_model=Message, dependencies=[Depends(require_csrf)])
def disable_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Message:
    user = db.get(User, user_id)
    if user and user.id != admin.id:
        user.is_active = False
        db.add(AuditLog(user_id=admin.id, action="admin.disable_user", entity_type="user", entity_id=user.id))
        db.commit()
    return Message(message="Account updated")
