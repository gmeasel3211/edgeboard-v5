from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.services.pipeline import RefreshPipeline

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")
pipeline = RefreshPipeline()


async def safe_full_refresh() -> None:
    delays = (0, 30, 120)
    for attempt, delay in enumerate(delays, start=1):
        if delay:
            await asyncio.sleep(delay)
        try:
            await pipeline.run_full()
            return
        except Exception:
            logger.exception("Refresh attempt %s of %s failed", attempt, len(delays))
    logger.error("EdgeBoard refresh exhausted all retry attempts")


def start_scheduler() -> None:
    if not settings.auto_refresh_enabled or scheduler.running:
        return
    scheduler.add_job(
        safe_full_refresh,
        "interval",
        minutes=max(5, settings.odds_refresh_minutes),
        id="full-refresh",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
