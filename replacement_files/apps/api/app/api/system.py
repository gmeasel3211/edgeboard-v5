from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Game, OddsSnapshot, Pick, RefreshRun, WeatherSnapshot

router = APIRouter(prefix="/system", tags=["System"])


def age_minutes(value):
    if not value:
        return None
    now = datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return round((now - value).total_seconds() / 60, 1)


@router.get("/status")
def status(db: Session = Depends(get_db)):
    database_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_ok = False

    runs = list(db.scalars(select(RefreshRun).order_by(RefreshRun.started_at.desc()).limit(20)).all())
    latest = {}
    for run in runs:
        latest.setdefault(run.job_name, run)

    last_odds = db.scalar(select(func.max(OddsSnapshot.captured_at)))
    last_weather = db.scalar(select(func.max(WeatherSnapshot.captured_at)))
    future_games = db.scalar(select(func.count(Game.id)).where(Game.starts_at >= datetime.now(timezone.utc))) or 0
    active_picks = db.scalar(select(func.count(Pick.id)).where(Pick.status == "pending")) or 0
    odds_rows = db.scalar(select(func.count(OddsSnapshot.id))) or 0

    def service(job):
        run = latest.get(job)
        return {
            "status": run.status if run else "waiting",
            "last_run_minutes_ago": age_minutes(run.finished_at) if run else None,
        }

    return {
        "services": {
            "api": {"status": "online"},
            "database": {"status": "healthy" if database_ok else "failed"},
            "scheduler": {
                "status": "running" if settings.auto_refresh_enabled else "disabled",
                "interval_minutes": settings.odds_refresh_minutes,
            },
            "mlb": service("mlb"),
            "odds": {**service("odds"), "last_data_minutes_ago": age_minutes(last_odds)},
            "weather": {**service("weather"), "last_data_minutes_ago": age_minutes(last_weather)},
        },
        "counts": {
            "upcoming_games": future_games,
            "odds_snapshots": odds_rows,
            "active_picks": active_picks,
            "bookmakers": len(settings.allowed_bookmakers),
        },
        "recent_runs": [{
            "job": run.job_name,
            "status": run.status,
            "summary": run.details or {},
            "error": {
                "message": run.error_message,
                "category": (run.details or {}).get("category", "unknown"),
                "retryable": True,
            } if run.error_message else None,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "duration_ms": (run.details or {}).get("duration_ms"),
        } for run in runs],
    }
