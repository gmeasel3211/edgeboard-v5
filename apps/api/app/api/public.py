from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Game, Recommendation
from ..services.metrics import performance_summary

router = APIRouter(prefix="/public", tags=["public"])
settings = get_settings()


def serialize_pick(pick: Recommendation, game: Game) -> dict:
    return {
        "id": pick.id,
        "game_id": pick.game_id,
        "card_date": pick.card_date,
        "matchup": f"{game.away_team} at {game.home_team}",
        "commence_time": game.commence_time,
        "market": pick.market,
        "selection": pick.selection,
        "line": pick.line,
        "bookmaker": pick.bookmaker,
        "price": pick.price,
        "model_probability": pick.model_probability,
        "market_probability": pick.market_probability,
        "fair_odds": pick.fair_odds,
        "edge": pick.edge,
        "expected_value": pick.expected_value,
        "confidence": pick.confidence,
        "data_quality": pick.data_quality,
        "score": pick.score,
        "grade": pick.grade,
        "units": pick.units,
        "is_official": pick.is_official,
        "result": pick.result,
        "profit_units": pick.profit_units,
        "clv": pick.clv,
        "reasons": pick.reasons_json[:2],
    }


@router.get("/status")
def status(db: Session = Depends(get_db)) -> dict:
    last_pick = db.scalar(select(Recommendation).order_by(desc(Recommendation.created_at)).limit(1))
    return {
        "name": "EdgeBoard",
        "sport": "MLB",
        "model_version": settings.model_version,
        "as_of": datetime.now(timezone.utc),
        "last_model_update": last_pick.created_at if last_pick else None,
        "books": ["FanDuel", "DraftKings"],
        "demo_mode": settings.demo_mode,
    }


@router.get("/record")
def record(db: Session = Depends(get_db)) -> dict:
    return performance_summary(db)


@router.get("/free-pick")
def free_pick(db: Session = Depends(get_db)) -> dict:
    pick = db.scalar(
        select(Recommendation)
        .where(Recommendation.is_official.is_(True))
        .order_by(desc(Recommendation.card_date), desc(Recommendation.score))
        .limit(1)
    )
    if not pick:
        return {"pick": None}
    game = db.get(Game, pick.game_id)
    return {"pick": serialize_pick(pick, game)} if game else {"pick": None}


@router.get("/pricing")
def pricing() -> dict:
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "features": ["Public model record", "One featured pick", "Weekly recap"],
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 29,
                "features": ["Full official card", "Game breakdowns", "Fair odds and EV", "Performance center"],
            },
            {
                "id": "elite",
                "name": "Elite",
                "price": 59,
                "features": ["Everything in Pro", "Full watchlist", "Advanced filters", "Priority alerts and exports"],
            },
        ]
    }
