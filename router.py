from __future__ import annotations

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import Message
from ..services.stripe_service import construct_event, process_event

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe", response_model=Message)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
) -> Message:
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Stripe signature missing")
    payload = await request.body()
    try:
        event = construct_event(payload, stripe_signature)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from exc
    process_event(db, event)
    return Message(message="received")
