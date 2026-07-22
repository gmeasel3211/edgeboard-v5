from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select, text
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import require_admin
from ..models import Game, OperationLog, Quote, Recommendation, User

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status")
def status(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    database = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database = "unhealthy"

    latest_quote = db.scalar(select(func.max(Quote.fetched_at)))
    latest_run = db.scalar(select(OperationLog).order_by(desc(OperationLog.started_at)).limit(1))
    operations = db.scalars(select(OperationLog).order_by(desc(OperationLog.started_at)).limit(15)).all()
    upcoming = db.scalar(select(func.count(Game.id)).where(Game.commence_time >= now)) or 0
    quote_count = db.scalar(select(func.count(Quote.id)).where(Quote.fetched_at >= now - timedelta(hours=24))) or 0
    picks = db.scalar(select(func.count(Recommendation.id)).where(Recommendation.is_official.is_(True), Recommendation.result.is_(None))) or 0
    books = db.scalar(select(func.count(func.distinct(Quote.bookmaker))).where(Quote.fetched_at >= now - timedelta(hours=24))) or 0

    quote_age = (now - latest_quote).total_seconds() / 60 if latest_quote else None
    return {
        "checked_at": now,
        "services": {
            "api": "healthy",
            "database": database,
            "scheduler": "healthy" if latest_run and latest_run.started_at >= now - timedelta(hours=1) else "stale",
            "mlb": "healthy" if latest_run and not any("MLB schedule" in e for e in (latest_run.summary_json or {}).get("errors", [])) else "degraded",
            "odds": "healthy" if quote_age is not None and quote_age <= 45 else "stale",
            "weather": "healthy" if latest_run and not any("weather" in e.lower() for e in (latest_run.summary_json or {}).get("errors", [])) else "degraded",
        },
        "counts": {"upcoming_games": upcoming, "odds_snapshots_24h": quote_count, "active_picks": picks, "bookmakers_24h": books},
        "freshness": {"latest_odds_at": latest_quote, "odds_age_minutes": round(quote_age, 1) if quote_age is not None else None},
        "recent_runs": [{
            "id": row.id, "operation": row.operation, "status": row.status, "started_at": row.started_at,
            "finished_at": row.finished_at, "triggered_by": row.triggered_by, "summary": row.summary_json or {}, "error": row.error_text,
        } for row in operations],
    }
