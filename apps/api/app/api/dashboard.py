from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user, require_paid
from ..models import Game, Projection, Recommendation, User
from ..schemas import DashboardResponse, PerformanceResponse, PickOut
from ..services.metrics import performance_breakdown, performance_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
_ET = ZoneInfo("America/New_York")


def pick_out(pick: Recommendation, game: Game, include_reasons: bool = True) -> PickOut:
    return PickOut(
        id=pick.id,
        game_id=pick.game_id,
        card_date=pick.card_date,
        matchup=f"{game.away_team} at {game.home_team}",
        commence_time=game.commence_time,
        market=pick.market,
        selection=pick.selection,
        line=pick.line,
        bookmaker=pick.bookmaker,
        price=pick.price,
        model_probability=pick.model_probability,
        market_probability=pick.market_probability,
        fair_odds=pick.fair_odds,
        edge=pick.edge,
        expected_value=pick.expected_value,
        confidence=pick.confidence,
        data_quality=pick.data_quality,
        score=pick.score,
        grade=pick.grade,
        units=pick.units,
        is_official=pick.is_official,
        result=pick.result,
        profit_units=pick.profit_units,
        clv=pick.clv,
        reasons=pick.reasons_json if include_reasons else [],
    )


@router.get("/today", response_model=DashboardResponse)
def today_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    today = datetime.now(timezone.utc).astimezone(_ET).date()
    official_rows = db.scalars(
        select(Recommendation)
        .where(Recommendation.card_date == today, Recommendation.is_official.is_(True))
        .order_by(desc(Recommendation.score))
    ).all()
    watch_rows = db.scalars(
        select(Recommendation)
        .where(Recommendation.card_date == today, Recommendation.is_official.is_(False), Recommendation.units > 0)
        .order_by(desc(Recommendation.score))
        .limit(30)
    ).all()
    is_paid = user.role == "admin" or user.tier in {"pro", "elite"}
    visible_official = official_rows if is_paid else official_rows[:1]
    visible_watch = watch_rows if user.role == "admin" or user.tier == "elite" else []
    games = {game.id: game for game in db.scalars(select(Game).where(Game.game_date == today)).all()}
    game_cards = []
    for game in sorted(games.values(), key=lambda item: item.commence_time):
        projection = db.scalar(
            select(Projection).where(Projection.game_id == game.id).order_by(desc(Projection.generated_at)).limit(1)
        )
        game_cards.append(
            {
                "id": game.id,
                "matchup": f"{game.away_team} at {game.home_team}",
                "commence_time": game.commence_time,
                "venue": game.venue,
                "status": game.status,
                "away_pitcher": game.away_pitcher,
                "home_pitcher": game.home_pitcher,
                "projected_score": {
                    "away": projection.away_runs if projection else None,
                    "home": projection.home_runs if projection else None,
                },
                "home_win_probability": projection.home_win_probability if projection and is_paid else None,
                "data_quality": projection.data_quality if projection and is_paid else None,
            }
        )
    return DashboardResponse(
        as_of=datetime.now(timezone.utc),
        tier=user.tier,
        record=performance_summary(db),
        official=[pick_out(pick, games[pick.game_id], include_reasons=is_paid) for pick in visible_official if pick.game_id in games],
        watchlist=[pick_out(pick, games[pick.game_id]) for pick in visible_watch if pick.game_id in games],
        games=game_cards,
    )


@router.get("/performance", response_model=PerformanceResponse)
def performance(
    _: User = Depends(require_paid),
    db: Session = Depends(get_db),
) -> PerformanceResponse:
    return PerformanceResponse(**performance_breakdown(db))


@router.get("/history")
def history(
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_paid),
    db: Session = Depends(get_db),
) -> dict:
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.is_official.is_(True))
        .order_by(desc(Recommendation.card_date), desc(Recommendation.created_at))
        .limit(limit)
    ).all()
    games = {game.id: game for game in db.scalars(select(Game).where(Game.id.in_([p.game_id for p in picks]))).all()}
    return {"picks": [pick_out(p, games[p.game_id]) for p in picks if p.game_id in games]}


@router.get("/games/{game_id}")
def game_detail(
    game_id: str,
    _: User = Depends(require_paid),
    db: Session = Depends(get_db),
) -> dict:
    game = db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    projection = db.scalar(
        select(Projection).where(Projection.game_id == game_id).order_by(desc(Projection.generated_at)).limit(1)
    )
    picks = db.scalars(
        select(Recommendation).where(Recommendation.game_id == game_id).order_by(desc(Recommendation.score))
    ).all()
    return {
        "game": {
            "id": game.id,
            "away_team": game.away_team,
            "home_team": game.home_team,
            "commence_time": game.commence_time,
            "venue": game.venue,
            "away_pitcher": game.away_pitcher,
            "home_pitcher": game.home_pitcher,
            "metadata": game.metadata_json,
        },
        "projection": {
            "away_runs": projection.away_runs,
            "home_runs": projection.home_runs,
            "away_win_probability": projection.away_win_probability,
            "home_win_probability": projection.home_win_probability,
            "total_mean": projection.total_mean,
            "data_quality": projection.data_quality,
            "confidence": projection.confidence,
            "reasons": projection.reasons_json,
            "inputs": projection.inputs_json,
        }
        if projection
        else None,
        "markets": [pick_out(pick, game) for pick in picks],
    }
