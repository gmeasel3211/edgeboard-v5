from __future__ import annotations

import logging

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_email(*, to: str, subject: str, html: str) -> None:
    if not settings.resend_api_key:
        logger.warning("Email provider not configured. Intended recipient=%s subject=%s", to, subject)
        return
    payload = {"from": settings.email_from, "to": [to], "subject": subject, "html": html}
    headers = {"Authorization": f"Bearer {settings.resend_api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://api.resend.com/emails", headers=headers, json=payload)
        response.raise_for_status()


async def send_verification_email(email: str, raw_token: str) -> None:
    url = f"{settings.frontend_url}/verify-email?token={raw_token}"
    await send_email(
        to=email,
        subject="Verify your EdgeBoard account",
        html=f"<p>Verify your account by opening <a href='{url}'>this secure link</a>. It expires in 24 hours.</p>",
    )


async def send_password_reset_email(email: str, raw_token: str) -> None:
    url = f"{settings.frontend_url}/reset-password?token={raw_token}"
    await send_email(
        to=email,
        subject="Reset your EdgeBoard password",
        html=f"<p>Reset your password by opening <a href='{url}'>this secure link</a>. It expires in one hour.</p>",
    )
