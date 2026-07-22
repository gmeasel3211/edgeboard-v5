from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import require_csrf, require_verified
from ..models import User
from ..schemas import CheckoutRequest, CheckoutResponse
from ..services.stripe_service import create_checkout_session, create_portal_session

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout", response_model=CheckoutResponse, dependencies=[Depends(require_csrf)])
def checkout(
    payload: CheckoutRequest,
    user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    try:
        return CheckoutResponse(url=create_checkout_session(db, user, payload.plan))
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/portal", response_model=CheckoutResponse, dependencies=[Depends(require_csrf)])
def portal(user: User = Depends(require_verified)) -> CheckoutResponse:
    try:
        return CheckoutResponse(url=create_portal_session(user))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
