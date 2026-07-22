from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import stripe
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import AuditLog, Subscription, User

settings = get_settings()
stripe.api_key = settings.stripe_secret_key


def price_for_tier(tier: str) -> str:
    mapping = {
        "pro": settings.stripe_price_pro_monthly,
        "elite": settings.stripe_price_elite_monthly,
    }
    price = mapping.get(tier, "")
    if not price:
        raise ValueError(f"Stripe price for {tier} is not configured")
    return price


def tier_for_price(price_id: str | None) -> str:
    if price_id and price_id == settings.stripe_price_elite_monthly:
        return "elite"
    if price_id and price_id == settings.stripe_price_pro_monthly:
        return "pro"
    return "free"


def create_checkout_session(db: Session, user: User, tier: str) -> str:
    if not settings.stripe_secret_key:
        raise ValueError("Stripe is not configured")
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.display_name, metadata={"user_id": user.id})
        user.stripe_customer_id = customer.id
        db.commit()
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": price_for_tier(tier), "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url}/pricing?canceled=1",
        client_reference_id=user.id,
        metadata={"user_id": user.id, "tier": tier},
        subscription_data={"metadata": {"user_id": user.id, "tier": tier}},
        allow_promotion_codes=True,
    )
    if not session.url:
        raise RuntimeError("Stripe did not return a checkout URL")
    return session.url


def create_portal_session(user: User) -> str:
    if not user.stripe_customer_id:
        raise ValueError("No Stripe customer exists for this account")
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{settings.frontend_url}/dashboard",
    )
    return session.url


def construct_event(payload: bytes, signature: str) -> stripe.Event:
    if not settings.stripe_webhook_secret:
        raise ValueError("Stripe webhook secret is not configured")
    return stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)


def process_event(db: Session, event: stripe.Event) -> None:
    existing = db.scalar(
        select(AuditLog).where(AuditLog.action == "stripe.webhook", AuditLog.entity_id == event.id)
    )
    if existing:
        return
    event_type = event.type
    obj: Any = event.data.object
    if event_type == "checkout.session.completed":
        user_id = obj.get("client_reference_id") or obj.get("metadata", {}).get("user_id")
        user = db.get(User, user_id) if user_id else None
        if user:
            user.stripe_customer_id = obj.get("customer") or user.stripe_customer_id
    elif event_type.startswith("customer.subscription."):
        _sync_subscription(db, obj)
    elif event_type in {"invoice.paid", "invoice.payment_failed"}:
        subscription_id = obj.get("subscription")
        if subscription_id:
            try:
                subscription_obj = stripe.Subscription.retrieve(subscription_id)
                _sync_subscription(db, subscription_obj)
            except Exception:
                pass
    db.add(
        AuditLog(
            action="stripe.webhook",
            entity_type="stripe_event",
            entity_id=event.id,
            metadata_json={"type": event_type},
        )
    )
    db.commit()


def _sync_subscription(db: Session, obj: Any) -> None:
    customer_id = obj.get("customer")
    metadata = obj.get("metadata", {}) or {}
    user_id = metadata.get("user_id")
    user = db.get(User, user_id) if user_id else db.scalar(select(User).where(User.stripe_customer_id == customer_id))
    if not user:
        return
    items = obj.get("items", {}).get("data", [])
    price_id = items[0].get("price", {}).get("id") if items else None
    product_id = items[0].get("price", {}).get("product") if items else None
    tier = metadata.get("tier") or tier_for_price(price_id)
    status = obj.get("status", "unknown")
    current_period_end = obj.get("current_period_end")
    period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc) if current_period_end else None
    provider_id = obj.get("id")
    record = db.scalar(select(Subscription).where(Subscription.provider_subscription_id == provider_id))
    if not record:
        record = Subscription(
            user_id=user.id,
            provider_subscription_id=provider_id,
            provider_customer_id=customer_id,
            status=status,
            tier=tier,
        )
        db.add(record)
    record.provider_customer_id = customer_id
    record.product_id = product_id
    record.price_id = price_id
    record.tier = tier
    record.status = status
    record.current_period_end = period_end
    record.cancel_at_period_end = bool(obj.get("cancel_at_period_end"))
    user.tier = tier if status in {"active", "trialing"} else "free"
