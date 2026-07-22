from __future__ import annotations

from datetime import date
from typing import Any

import httpx

BASE_URL = "https://statsapi.mlb.com/api"


class MLBClient:
    def __init__(self) -> None:
        self._team_cache: dict[tuple[int, int], dict[str, Any]] = {}
        self._pitcher_cache: dict[tuple[int, int], dict[str, Any]] = {}
        self._recent_cache: dict[tuple[int, str, str], dict[str, Any]] = {}

    async def schedule(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        params = {
            "sportId": 1,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "hydrate": "probablePitcher,venue,linescore,officials",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{BASE_URL}/v1/schedule", params=params)
            response.raise_for_status()
            payload = response.json()

        games: list[dict[str, Any]] = []
        for day in payload.get("dates", []):
            for game in day.get("games", []):
                teams = game.get("teams", {})
                away = teams.get("away", {})
                home = teams.get("home", {})
                venue = game.get("venue", {})
                official = next(
                    (
                        item.get("official", {}).get("fullName")
                        for item in game.get("officials", [])
                        if item.get("officialType") == "Home Plate"
                    ),
                    None,
                )
                games.append(
                    {
                        "game_pk": str(game.get("gamePk")),
                        "game_date": game.get("gameDate"),
                        "status": game.get("status", {}).get("abstractGameState", "Preview").lower(),
                        "away_team": away.get("team", {}).get("name"),
                        "home_team": home.get("team", {}).get("name"),
                        "away_team_id": away.get("team", {}).get("id"),
                        "home_team_id": home.get("team", {}).get("id"),
                        "away_pitcher": away.get("probablePitcher", {}).get("fullName"),
                        "home_pitcher": home.get("probablePitcher", {}).get("fullName"),
                        "away_pitcher_id": away.get("probablePitcher", {}).get("id"),
                        "home_pitcher_id": home.get("probablePitcher", {}).get("id"),
                        "away_score": away.get("score"),
                        "home_score": home.get("score"),
                        "venue": venue.get("name"),
                        "umpire": official,
                    }
                )
        return games

    async def team_stats(self, team_id: int | None, season: int) -> dict[str, Any]:
        if not team_id:
            return self.neutral_team()
        cache_key = (team_id, season)
        if cache_key in self._team_cache:
            return self._team_cache[cache_key]
        params = {"stats": "season", "group": "hitting,pitching", "season": season}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{BASE_URL}/v1/teams/{team_id}/stats", params=params)
            response.raise_for_status()
            payload = response.json()
        hitting: dict[str, Any] = {}
        pitching: dict[str, Any] = {}
        for block in payload.get("stats", []):
            group = block.get("group", {}).get("displayName")
            splits = block.get("splits", [])
            stat = splits[0].get("stat", {}) if splits else {}
            if group == "hitting":
                hitting = stat
            elif group == "pitching":
                pitching = stat
        games = max(int(hitting.get("gamesPlayed", 0) or 0), 1)
        wins = float(pitching.get("wins", 0) or 0)
        losses = float(pitching.get("losses", 0) or 0)
        runs_for = float(hitting.get("runs", 0) or 0)
        runs_against = float(pitching.get("runs", 0) or 0)
        result = {
            "games": games,
            "win_pct": wins / max(wins + losses, 1),
            "runs_for_game": runs_for / games,
            "runs_against_game": runs_against / games,
            "ops": float(hitting.get("ops", 0.710) or 0.710),
            "era": float(pitching.get("era", 4.50) or 4.50),
            "whip": float(pitching.get("whip", 1.30) or 1.30),
            "quality": 82 if games >= 40 else 68,
        }
        rf2 = max(runs_for**2, 1)
        ra2 = max(runs_against**2, 1)
        result["pythag"] = rf2 / (rf2 + ra2)
        self._team_cache[cache_key] = result
        return result

    async def team_recent_stats(
        self, team_id: int | None, start_date: date, end_date: date
    ) -> dict[str, Any]:
        if not team_id:
            return {"win_pct": 0.5, "runs_for_game": 4.5, "runs_against_game": 4.5, "quality": 35}
        cache_key = (team_id, start_date.isoformat(), end_date.isoformat())
        if cache_key in self._recent_cache:
            return self._recent_cache[cache_key]
        params = {
            "stats": "byDateRange",
            "group": "hitting,pitching",
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{BASE_URL}/v1/teams/{team_id}/stats", params=params)
                response.raise_for_status()
                payload = response.json()
            hitting: dict[str, Any] = {}
            pitching: dict[str, Any] = {}
            for block in payload.get("stats", []):
                group = block.get("group", {}).get("displayName")
                splits = block.get("splits", [])
                stat = splits[0].get("stat", {}) if splits else {}
                if group == "hitting":
                    hitting = stat
                elif group == "pitching":
                    pitching = stat
            games = max(int(hitting.get("gamesPlayed", 0) or 0), 1)
            wins = float(pitching.get("wins", 0) or 0)
            losses = float(pitching.get("losses", 0) or 0)
            result = {
                "win_pct": wins / max(wins + losses, 1),
                "runs_for_game": float(hitting.get("runs", 0) or 0) / games,
                "runs_against_game": float(pitching.get("runs", 0) or 0) / games,
                "quality": 72 if games >= 7 else 48,
            }
        except Exception:
            result = {"win_pct": 0.5, "runs_for_game": 4.5, "runs_against_game": 4.5, "quality": 30}
        self._recent_cache[cache_key] = result
        return result

    async def pitcher_stats(self, pitcher_id: int | None, season: int) -> dict[str, Any]:
        if not pitcher_id:
            return self.neutral_pitcher()
        cache_key = (pitcher_id, season)
        if cache_key in self._pitcher_cache:
            return self._pitcher_cache[cache_key]
        params = {"stats": "season", "group": "pitching", "season": season}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{BASE_URL}/v1/people/{pitcher_id}/stats", params=params)
                response.raise_for_status()
                payload = response.json()
            splits = payload.get("stats", [{}])[0].get("splits", [])
            stat = splits[0].get("stat", {}) if splits else {}
            innings = float(str(stat.get("inningsPitched", "0")).replace(".1", ".333").replace(".2", ".667"))
            result = {
                "era": float(stat.get("era", 4.50) or 4.50),
                "whip": float(stat.get("whip", 1.30) or 1.30),
                "k9": 9 * float(stat.get("strikeOuts", 0) or 0) / max(innings, 1),
                "bb9": 9 * float(stat.get("baseOnBalls", 0) or 0) / max(innings, 1),
                "innings": innings,
                "quality": 88 if innings >= 60 else 68 if innings >= 25 else 48,
            }
        except Exception:
            result = self.neutral_pitcher()
        self._pitcher_cache[cache_key] = result
        return result

    @staticmethod
    def neutral_team() -> dict[str, Any]:
        return {
            "games": 0,
            "win_pct": 0.5,
            "pythag": 0.5,
            "runs_for_game": 4.5,
            "runs_against_game": 4.5,
            "ops": 0.710,
            "era": 4.5,
            "whip": 1.30,
            "quality": 30,
        }

    @staticmethod
    def neutral_pitcher() -> dict[str, Any]:
        return {"era": 4.5, "whip": 1.30, "k9": 8.5, "bb9": 3.2, "innings": 0, "quality": 30}
