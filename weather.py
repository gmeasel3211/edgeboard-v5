from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from ..models import Game, Quote, Recommendation
from .math_utils import american_to_implied, profit_for_units


def _grade_pick(pick: Recommendation, game: Game) -> str | None:
    if game.away_score is None or game.home_score is None:
        return None
    away = game.away_score
    home = game.home_score
    if pick.market == "h2h":
        winner = game.home_team if home > away else game.away_team
        return "W" if pick.selection == winner else "L"
    if pick.market == "spreads" and pick.line is not None:
        selected_score = away if pick.selection == game.away_team else home
        opponent_score = home if pick.selection == game.away_team else away
        adjusted = selected_score + pick.line
        if adjusted > opponent_score:
            return "W"
        if adjusted < opponent_score:
            return "L"
        return "P"
    if pick.market == "totals" and pick.line is not None:
        total = away + home
        if total == pick.line:
            return "P"
        if pick.selection.lower() == "over":
            return "W" if total > pick.line else "L"
        return "W" if total < pick.line else "L"
    return None


def _closing_quote(db: Session, pick: Recommendation, game: Game) -> Quote | None:
    conditions = [
        Quote.game_id == pick.game_id,
        Quote.market == pick.market,
        Quote.selection == pick.selection,
        Quote.bookmaker == pick.bookmaker,
        Quote.fetched_at <= game.commence_time,
    ]
    if pick.line is None:
        conditions.append(Quote.line.is_(None))
    else:
        conditions.append(Quote.line == pick.line)
    return db.scalar(select(Quote).where(and_(*conditions)).order_by(desc(Quote.fetched_at)).limit(1))


def grade_official_picks(db: Session) -> dict[str, int]:
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.is_official.is_(True), Recommendation.result.is_(None))
        .order_by(Recommendation.card_date)
    ).all()
    graded = 0
    for pick in picks:
        game = db.get(Game, pick.game_id)
        if not game or game.status not in {"final", "completed", "game over"}:
            continue
        result = _grade_pick(pick, game)
        if result is None:
            continue
        pick.result = result
        pick.settled_at = datetime.now(timezone.utc)
        pick.profit_units = (
            profit_for_units(pick.units, pick.price)
            if result == "W"
            else -pick.units
            if result == "L"
            else 0.0
        )
        close = _closing_quote(db, pick, game)
        if close:
            pick.closing_price = close.price
            pick.clv = american_to_implied(close.price) - american_to_implied(pick.price)
        graded += 1
    db.commit()
    return {"graded": graded, "pending": max(len(picks) - graded, 0)}
