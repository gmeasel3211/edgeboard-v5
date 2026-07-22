from __future__ import annotations

import csv
import io
from dataclasses import asdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..db import SessionLocal, get_db
from ..dependencies import require_admin, require_cron_secret, require_csrf
from ..models import AuditLog, Game, OperationLog, Recommendation, User
from ..schemas import AdminOperationRequest, SettingUpdate
from ..services.grading import grade_official_picks
from ..services.pipeline import Pipeline
from ..services.settings_service import get_policy, update_policy

router = APIRouter(prefix="/admin", tags=["admin"])
pipeline = Pipeline()
_ET = ZoneInfo("America/New_York")


@router.get("/overview")
def overview(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    operations = db.scalars(select(OperationLog).order_by(desc(OperationLog.started_at)).limit(20)).all()
    return {
        "policy": asdict(get_policy(db)),
        "operations": [
            {
                "id": row.id,
                "operation": row.operation,
                "status": row.status,
                "started_at": row.started_at,
                "finished_at": row.finished_at,
                "triggered_by": row.triggered_by,
                "summary": row.summary_json,
                "error": row.error_text,
            }
            for row in operations
        ],
    }


@router.post("/refresh", dependencies=[Depends(require_csrf)])
async def refresh(
    payload: AdminOperationRequest,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    result = await pipeline.refresh(db, force_official=payload.force_official, triggered_by=user.email)
    db.add(AuditLog(user_id=user.id, action="admin.refresh", metadata_json=payload.model_dump()))
    db.commit()
    return result


@router.post("/cron/refresh", dependencies=[Depends(require_cron_secret)])
async def cron_refresh(
    payload: AdminOperationRequest,
    db: Session = Depends(get_db),
) -> dict:
    return await pipeline.refresh(db, force_official=payload.force_official, triggered_by="render-cron")


@router.post("/grade", dependencies=[Depends(require_csrf)])
def grade(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    result = grade_official_picks(db)
    db.add(AuditLog(user_id=user.id, action="admin.grade", metadata_json=result))
    db.commit()
    return result


@router.post("/settings", dependencies=[Depends(require_csrf)])
def settings_update(
    payload: SettingUpdate,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    try:
        policy = update_policy(db, payload.values, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.add(AuditLog(user_id=user.id, action="admin.settings", metadata_json=payload.values))
    db.commit()
    return asdict(policy)


@router.get("/export/today.csv")
def export_today(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> StreamingResponse:
    today = datetime.now(timezone.utc).astimezone(_ET).date()
    picks = db.scalars(
        select(Recommendation).where(
            Recommendation.card_date == today,
            Recommendation.is_official.is_(True),
        )
    ).all()
    games = {game.id: game for game in db.scalars(select(Game).where(Game.id.in_([p.game_id for p in picks]))).all()}
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(
        ["date", "matchup", "market", "selection", "line", "bookmaker", "price", "edge", "ev", "grade", "units"]
    )
    for pick in picks:
        game = games.get(pick.game_id)
        writer.writerow(
            [
                pick.card_date,
                f"{game.away_team} at {game.home_team}" if game else pick.game_id,
                pick.market,
                pick.selection,
                pick.line,
                pick.bookmaker,
                pick.price,
                round(pick.edge, 4),
                round(pick.expected_value, 4),
                pick.grade,
                pick.units,
            ]
        )
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f'attachment; filename="edgeboard-{today}.csv"'
    return response
