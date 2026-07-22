from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Recommendation


def performance_summary(db: Session) -> dict[str, Any]:
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.is_official.is_(True))
        .order_by(Recommendation.card_date, Recommendation.created_at)
    ).all()
    settled = [pick for pick in picks if pick.result in {"W", "L", "P"}]
    wins = sum(pick.result == "W" for pick in settled)
    losses = sum(pick.result == "L" for pick in settled)
    pushes = sum(pick.result == "P" for pick in settled)
    units_risked = sum(pick.units for pick in settled if pick.result != "P")
    profit = sum(pick.profit_units or 0 for pick in settled)
    clv_values = [pick.clv for pick in settled if pick.clv is not None]
    return {
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "pending": len(picks) - len(settled),
        "units": round(profit, 2),
        "units_risked": round(units_risked, 2),
        "roi": profit / units_risked if units_risked else 0.0,
        "win_rate": wins / max(wins + losses, 1),
        "average_clv": sum(clv_values) / len(clv_values) if clv_values else None,
        "total_official": len(picks),
    }


def performance_breakdown(db: Session) -> dict[str, Any]:
    picks = db.scalars(
        select(Recommendation)
        .where(Recommendation.is_official.is_(True), Recommendation.result.is_not(None))
        .order_by(Recommendation.card_date)
    ).all()
    daily_map: dict[date, dict[str, Any]] = defaultdict(
        lambda: {"wins": 0, "losses": 0, "pushes": 0, "units": 0.0, "risked": 0.0}
    )
    market_map: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"wins": 0, "losses": 0, "pushes": 0, "units": 0.0, "risked": 0.0}
    )
    grade_map: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"wins": 0, "losses": 0, "pushes": 0, "units": 0.0, "risked": 0.0}
    )
    cumulative = 0.0
    for pick in picks:
        result_key = {"W": "wins", "L": "losses", "P": "pushes"}[pick.result or "P"]
        for bucket in (daily_map[pick.card_date], market_map[pick.market], grade_map[pick.grade]):
            bucket[result_key] += 1
            bucket["units"] += pick.profit_units or 0.0
            bucket["risked"] += pick.units if pick.result != "P" else 0.0
    daily: list[dict[str, Any]] = []
    for day in sorted(daily_map):
        row = daily_map[day]
        cumulative += row["units"]
        daily.append(
            {
                "date": day.isoformat(),
                **{key: round(value, 2) if isinstance(value, float) else value for key, value in row.items()},
                "cumulative_units": round(cumulative, 2),
                "roi": row["units"] / row["risked"] if row["risked"] else 0.0,
            }
        )

    def flatten(mapping: dict[str, dict[str, Any]], label: str) -> list[dict[str, Any]]:
        output = []
        for name, row in sorted(mapping.items()):
            output.append(
                {
                    label: name,
                    **{key: round(value, 2) if isinstance(value, float) else value for key, value in row.items()},
                    "roi": row["units"] / row["risked"] if row["risked"] else 0.0,
                }
            )
        return output

    return {
        "summary": performance_summary(db),
        "daily": daily,
        "by_market": flatten(market_map, "market"),
        "by_grade": flatten(grade_map, "grade"),
    }
