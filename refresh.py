from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from ..config import get_settings
from .math_utils import american_to_implied

BASE_URL = "https://api.the-odds-api.com/v4"
ALLOWED_BOOKS = {"fanduel", "draftkings"}
ALLOWED_MARKETS = {"h2h", "spreads", "totals"}


class OddsClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_mlb_odds(self) -> list[dict[str, Any]]:
        if not self.settings.odds_api_key:
            return []
        params = {
            "apiKey": self.settings.odds_api_key,
            "bookmakers": ",".join(sorted(ALLOWED_BOOKS)),
            "markets": ",".join(sorted(ALLOWED_MARKETS)),
            "oddsFormat": "american",
            "dateFormat": "iso",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{BASE_URL}/sports/baseball_mlb/odds", params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def flatten(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        fetched_at = datetime.now(timezone.utc)
        rows: list[dict[str, Any]] = []
        for event in events:
            for bookmaker in event.get("bookmakers", []):
                book = bookmaker.get("key")
                if book not in ALLOWED_BOOKS:
                    continue
                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")
                    if market_key not in ALLOWED_MARKETS:
                        continue
                    for outcome in market.get("outcomes", []):
                        price = int(outcome["price"])
                        rows.append(
                            {
                                "provider_game_id": event.get("id"),
                                "commence_time": event["commence_time"],
                                "away_team": event["away_team"],
                                "home_team": event["home_team"],
                                "bookmaker": book,
                                "market": market_key,
                                "selection": outcome["name"],
                                "line": outcome.get("point"),
                                "price": price,
                                "implied_probability": american_to_implied(price),
                                "fetched_at": fetched_at,
                            }
                        )
        return rows
