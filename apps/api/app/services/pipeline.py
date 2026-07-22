from __future__ import annotations

import asyncio
import json
from time import perf_counter
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import delete, desc, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Game, OperationLog, Projection, Quote, Recommendation
from .grading import grade_official_picks
from .math_utils import american_to_implied, no_vig_probabilities
from .mlb import MLBClient
from .model import ModelEngine
from .odds import OddsClient
from .parks import PARKS
from .settings_service import get_policy
from .weather import WeatherClient

settings = get_settings()
_ET = ZoneInfo("America/New_York")
_PROCESS_LOCK = asyncio.Lock()
_LOCK_ID = 337_003_001

TEAM_ALIASES = {
    "oakland athletics": "Athletics",
    "athletics": "Athletics",
    "tampa bay rays": "Tampa Bay Rays",
}


def canonical_team(name: str | None) -> str:
    if not name:
        return "Unknown"
    return TEAM_ALIASES.get(name.strip().lower(), name.strip())


def game_key(game_date: date, away: str, home: str) -> str:
    return f"mlb:{game_date.isoformat()}:{away.lower().replace(' ', '-')}:{home.lower().replace(' ', '-')}"


class Pipeline:
    def __init__(self) -> None:
        self.odds = OddsClient()
        self.mlb = MLBClient()
        self.weather = WeatherClient()
        self.engine = ModelEngine(settings.model_simulations)

    def _try_database_lock(self, db: Session) -> bool:
        if db.bind and db.bind.dialect.name == "postgresql":
            return bool(db.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": _LOCK_ID}))
        return True

    def _release_database_lock(self, db: Session) -> None:
        if db.bind and db.bind.dialect.name == "postgresql":
            db.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": _LOCK_ID})

    async def refresh(self, db: Session, *, force_official: bool = False, triggered_by: str = "system") -> dict[str, Any]:
        async with _PROCESS_LOCK:
            if not self._try_database_lock(db):
                return {"status": "skipped", "reason": "Another refresh is already running"}
            operation = OperationLog(operation="refresh", status="running", triggered_by=triggered_by)
            db.add(operation)
            db.commit()
            started = perf_counter()
            try:
                result = await self._refresh_inner(db, force_official=force_official)
                result["duration_ms"] = round((perf_counter() - started) * 1000)
                operation.status = "success"
                operation.summary_json = result
                operation.finished_at = datetime.now(timezone.utc)
                db.commit()
                return result
            except Exception as exc:
                db.rollback()
                operation = db.get(OperationLog, operation.id)
                if operation:
                    category, friendly = self._classify_error(exc)
                    operation.status = "failed"
                    operation.summary_json = {
                        "category": category,
                        "duration_ms": round((perf_counter() - started) * 1000),
                    }
                    operation.error_text = friendly
                    operation.finished_at = datetime.now(timezone.utc)
                    db.commit()
                raise
            finally:
                self._release_database_lock(db)

    @staticmethod
    def _classify_error(exc: Exception) -> tuple[str, str]:
        message = str(exc).lower()
        if isinstance(exc, IntegrityError) or "duplicate key" in message or "unique constraint" in message:
            return "database_conflict", "A duplicate database record was detected and rolled back safely."
        if "timeout" in message:
            return "provider_timeout", "A data provider timed out. EdgeBoard will retry automatically."
        if "401" in message or "403" in message or "api key" in message:
            return "authentication", "A provider credential was rejected. Check the Render environment variables."
        if "429" in message or "quota" in message or "rate limit" in message:
            return "rate_limit", "A provider usage limit was reached. The next refresh will try again."
        if "connection" in message or "network" in message or "dns" in message:
            return "network", "A provider connection failed. EdgeBoard will retry automatically."
        return "unknown", "The refresh failed unexpectedly. Technical details remain in the server logs."

    async def _refresh_inner(self, db: Session, *, force_official: bool) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        today = now.astimezone(_ET).date()
        season = today.year
        errors: list[str] = []
        try:
            schedule = await self.mlb.schedule(today - timedelta(days=10), today + timedelta(days=2))
        except Exception as exc:
            schedule = []
            errors.append(f"MLB schedule: {exc}")
        try:
            odds_events = await self.odds.fetch_mlb_odds()
        except Exception as exc:
            odds_events = []
            errors.append(f"Odds API: {exc}")
        if not odds_events and settings.demo_mode:
            odds_events = self._demo_events(schedule, now)

        schedule_map = self._schedule_map(schedule)
        odds_rows = self.odds.flatten(odds_events)

        self._upsert_games(db, odds_events, schedule_map, now)
        self._update_past_scores(db, schedule)
        self._insert_quotes(db, odds_rows)
        db.commit()

        grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in odds_rows:
            commence = datetime.fromisoformat(row["commence_time"].replace("Z", "+00:00"))
            key = game_key(
                commence.astimezone(_ET).date(),
                canonical_team(row["away_team"]),
                canonical_team(row["home_team"]),
            )
            grouped_rows[key].append(row)

        if force_official:
            for prior in db.scalars(
                select(Recommendation).where(
                    Recommendation.card_date == today,
                    Recommendation.is_official.is_(True),
                    Recommendation.result.is_(None),
                )
            ).all():
                prior.is_official = False
            db.flush()
        db.execute(
            delete(Recommendation).where(
                Recommendation.card_date == today,
                Recommendation.is_official.is_(False),
            )
        )
        db.commit()

        candidates_created = 0
        projections_created = 0
        for game_id, rows in grouped_rows.items():
            game = db.get(Game, game_id)
            if not game or game.game_date != today:
                continue
            market_candidates = self._best_candidates(rows)
            if not market_candidates:
                continue
            market_home = self._market_home_probability(rows, game.home_team)
            meta = schedule_map.get(game_id, {})
            park_name, lat, lon, park_factor = PARKS.get(
                game.home_team,
                (game.venue or "Unknown", game.latitude, game.longitude, 1.0),
            )
            game.venue = park_name
            game.latitude = lat
            game.longitude = lon
            away_team, home_team, away_recent, home_recent, away_pitcher, home_pitcher, weather = await asyncio.gather(
                self.mlb.team_stats(game.away_team_id, season),
                self.mlb.team_stats(game.home_team_id, season),
                self.mlb.team_recent_stats(game.away_team_id, today - timedelta(days=14), today - timedelta(days=1)),
                self.mlb.team_recent_stats(game.home_team_id, today - timedelta(days=14), today - timedelta(days=1)),
                self.mlb.pitcher_stats(game.away_pitcher_id, season),
                self.mlb.pitcher_stats(game.home_pitcher_id, season),
                self.weather.forecast_for(lat, lon, game.commence_time),
            )
            away_rest, home_rest = self._rest_days(schedule, game)
            projection_result = self.engine.project_game(
                game_id=game.id,
                away_team_name=game.away_team,
                home_team_name=game.home_team,
                away_team=away_team,
                home_team=home_team,
                away_recent=away_recent,
                home_recent=home_recent,
                away_pitcher=away_pitcher,
                home_pitcher=home_pitcher,
                weather=weather,
                park_factor=park_factor,
                away_rest_days=away_rest,
                home_rest_days=home_rest,
                market_home_probability=market_home,
                candidates=market_candidates,
            )
            projection = Projection(
                game_id=game.id,
                model_version=settings.model_version,
                generated_at=now,
                away_runs=projection_result.away_runs,
                home_runs=projection_result.home_runs,
                away_win_probability=projection_result.away_win_probability,
                home_win_probability=projection_result.home_win_probability,
                total_mean=projection_result.total_mean,
                data_quality=projection_result.data_quality,
                confidence=projection_result.confidence,
                market_disagreement=projection_result.market_disagreement,
                simulation_count=projection_result.simulations,
                reasons_json=projection_result.reasons,
                inputs_json=projection_result.inputs,
                probabilities_json=projection_result.probabilities,
            )
            db.add(projection)
            db.flush()
            projections_created += 1

            policy = get_policy(db)
            for candidate in market_candidates:
                key = self.engine.candidate_key(candidate["market"], candidate["selection"], candidate.get("line"))
                model_probability = projection_result.probabilities.get(key)
                if model_probability is None:
                    continue
                evaluation = self.engine.evaluate_candidate(
                    model_probability=model_probability,
                    market_probability=candidate["market_probability"],
                    odds=candidate["price"],
                    confidence=projection_result.confidence,
                    data_quality=projection_result.data_quality,
                    policy=policy,
                    force=force_official,
                )
                recommendation = Recommendation(
                    game_id=game.id,
                    projection_id=projection.id,
                    card_date=today,
                    market=candidate["market"],
                    selection=candidate["selection"],
                    line=candidate.get("line"),
                    bookmaker=candidate["bookmaker"],
                    price=candidate["price"],
                    model_probability=model_probability,
                    market_probability=candidate["market_probability"],
                    fair_odds=evaluation["fair_odds"],
                    edge=evaluation["edge"],
                    expected_value=evaluation["expected_value"],
                    confidence=projection_result.confidence,
                    data_quality=projection_result.data_quality,
                    score=evaluation["score"],
                    grade=evaluation["grade"],
                    units=evaluation["units"],
                    is_official=False,
                    reasons_json=[
                        f"Best tracked price: {candidate['bookmaker']} at {candidate['price']:+d}.",
                        f"Break-even probability is {american_to_implied(candidate['price']) * 100:.1f}%; the model projects {model_probability * 100:.1f}%.",
                        f"Model edge versus the no-vig market is {evaluation['edge'] * 100:.1f} percentage points with {evaluation['expected_value'] * 100:.1f}% estimated EV.",
                        *(projection_result.reasons[:3]),
                        "Risk: probable pitchers, confirmed lineups, bullpen availability, injuries, weather, and price movement can change the projection before first pitch.",
                    ],
                )
                db.add(recommendation)
                candidates_created += 1
            game.metadata_json = {
                **(game.metadata_json or {}),
                "umpire": meta.get("umpire"),
                "weather": weather,
                "park_factor": park_factor,
                "rest": {"away": away_rest, "home": home_rest},
            }
            db.commit()

        official_created = self._select_official_card(db, today, force_official)
        grading = grade_official_picks(db)
        return {
            "status": "ok",
            "games": len(grouped_rows),
            "projections": projections_created,
            "candidates": candidates_created,
            "official_created": official_created,
            "graded": grading["graded"],
            "errors": errors,
            "refreshed_at": now.isoformat(),
        }

    def _upsert_games(
        self,
        db: Session,
        events: list[dict[str, Any]],
        schedule_map: dict[str, dict[str, Any]],
        now: datetime,
    ) -> None:
        for event in events:
            commence = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            game_date = commence.astimezone(_ET).date()
            away = canonical_team(event["away_team"])
            home = canonical_team(event["home_team"])
            key = game_key(game_date, away, home)
            league = schedule_map.get(key, {})
            venue, lat, lon, _ = PARKS.get(home, (league.get("venue"), None, None, 1.0))
            game = db.get(Game, key)
            if not game:
                game = Game(
                    id=key,
                    sport="mlb",
                    game_date=game_date,
                    commence_time=commence,
                    away_team=away,
                    home_team=home,
                )
                db.add(game)
            game.commence_time = commence
            game.provider_game_id = event.get("id")
            game.league_game_id = league.get("game_pk")
            game.away_team_id = league.get("away_team_id")
            game.home_team_id = league.get("home_team_id")
            game.away_pitcher = league.get("away_pitcher")
            game.home_pitcher = league.get("home_pitcher")
            game.away_pitcher_id = league.get("away_pitcher_id")
            game.home_pitcher_id = league.get("home_pitcher_id")
            game.venue = venue
            game.latitude = lat
            game.longitude = lon
            game.status = league.get("status", game.status)
            game.away_score = league.get("away_score")
            game.home_score = league.get("home_score")
            game.updated_at = now

    def _insert_quotes(self, db: Session, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        game_ids = set()
        normalized: list[tuple[dict[str, Any], str]] = []
        for row in rows:
            commence = datetime.fromisoformat(row["commence_time"].replace("Z", "+00:00"))
            key = game_key(
                commence.astimezone(_ET).date(),
                canonical_team(row["away_team"]),
                canonical_team(row["home_team"]),
            )
            if db.get(Game, key):
                game_ids.add(key)
                normalized.append((row, key))

        existing = {
            (q.game_id, q.bookmaker, q.market, q.selection, q.line, q.price, q.fetched_at)
            for q in db.scalars(select(Quote).where(Quote.game_id.in_(game_ids))).all()
        } if game_ids else set()

        for row, key in normalized:
            selection = canonical_team(row["selection"]) if row["market"] != "totals" else row["selection"]
            quote_key = (
                key, row["bookmaker"], row["market"], selection,
                row.get("line"), row["price"], row["fetched_at"],
            )
            if quote_key in existing:
                continue
            existing.add(quote_key)
            db.add(Quote(
                game_id=key,
                bookmaker=row["bookmaker"],
                market=row["market"],
                selection=selection,
                line=row.get("line"),
                price=row["price"],
                implied_probability=row["implied_probability"],
                fetched_at=row["fetched_at"],
            ))

    def _update_past_scores(self, db: Session, schedule: list[dict[str, Any]]) -> None:
        for item in schedule:
            if not item.get("away_team") or not item.get("home_team") or not item.get("game_date"):
                continue
            commence = datetime.fromisoformat(item["game_date"].replace("Z", "+00:00"))
            key = game_key(
                commence.astimezone(_ET).date(),
                canonical_team(item["away_team"]),
                canonical_team(item["home_team"]),
            )
            game = db.get(Game, key)
            if game:
                game.status = item.get("status", game.status)
                game.away_score = item.get("away_score")
                game.home_score = item.get("home_score")

    def _schedule_map(self, schedule: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        output = {}
        for item in schedule:
            if not item.get("away_team") or not item.get("home_team") or not item.get("game_date"):
                continue
            commence = datetime.fromisoformat(item["game_date"].replace("Z", "+00:00"))
            key = game_key(
                commence.astimezone(_ET).date(),
                canonical_team(item["away_team"]),
                canonical_team(item["home_team"]),
            )
            output[key] = item
        return output

    def _rest_days(self, schedule: list[dict[str, Any]], game: Game) -> tuple[int, int]:
        previous: dict[str, date] = {}
        for item in schedule:
            if not item.get("game_date"):
                continue
            day = datetime.fromisoformat(item["game_date"].replace("Z", "+00:00")).astimezone(_ET).date()
            if day >= game.game_date:
                continue
            for team in (canonical_team(item.get("away_team")), canonical_team(item.get("home_team"))):
                if team in {game.away_team, game.home_team} and (team not in previous or day > previous[team]):
                    previous[team] = day
        away_rest = (game.game_date - previous[game.away_team]).days - 1 if game.away_team in previous else 2
        home_rest = (game.game_date - previous[game.home_team]).days - 1 if game.home_team in previous else 2
        return max(away_rest, 0), max(home_rest, 0)

    def _market_home_probability(self, rows: list[dict[str, Any]], home_team: str) -> float | None:
        values = []
        by_book: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            if row["market"] == "h2h":
                by_book[row["bookmaker"]].append(row)
        for book_rows in by_book.values():
            if len(book_rows) < 2:
                continue
            implied = [item["implied_probability"] for item in book_rows[:2]]
            fair = no_vig_probabilities(implied)
            for item, probability in zip(book_rows[:2], fair, strict=False):
                if canonical_team(item["selection"]) == home_team:
                    values.append(probability)
        return sum(values) / len(values) if values else None

    def _best_candidates(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        canonical_rows = []
        for row in rows:
            canonical_rows.append(
                {
                    **row,
                    "selection": canonical_team(row["selection"]) if row["market"] != "totals" else row["selection"],
                }
            )
        pair_probabilities: dict[tuple[str, str, float | None], list[float]] = defaultdict(list)
        by_pair: dict[tuple[str, str, float | None], list[dict[str, Any]]] = defaultdict(list)
        for row in canonical_rows:
            pair_line = None if row["market"] == "h2h" else abs(float(row["line"])) if row["market"] == "spreads" and row["line"] is not None else row["line"]
            by_pair[(row["bookmaker"], row["market"], pair_line)].append(row)
        for pair_rows in by_pair.values():
            if len(pair_rows) < 2:
                continue
            fair = no_vig_probabilities([item["implied_probability"] for item in pair_rows])
            for item, probability in zip(pair_rows, fair, strict=False):
                pair_probabilities[(item["market"], item["selection"], item.get("line"))].append(probability)

        best: dict[tuple[str, str, float | None], dict[str, Any]] = {}
        for row in canonical_rows:
            key = (row["market"], row["selection"], row.get("line"))
            if key not in best or row["price"] > best[key]["price"]:
                best[key] = row
        output = []
        for key, row in best.items():
            probabilities = pair_probabilities.get(key, [])
            market_probability = sum(probabilities) / len(probabilities) if probabilities else row["implied_probability"]
            output.append({**row, "market_probability": market_probability})
        return output

    def _select_official_card(self, db: Session, card_date: date, force: bool) -> int:
        existing = db.scalars(
            select(Recommendation).where(
                Recommendation.card_date == card_date,
                Recommendation.is_official.is_(True),
            )
        ).all()
        if existing and not force:
            return 0
        if force:
            for pick in existing:
                if pick.result is None:
                    pick.is_official = False
            db.commit()
        policy = get_policy(db)
        candidates = db.scalars(
            select(Recommendation)
            .where(
                Recommendation.card_date == card_date,
                Recommendation.is_official.is_(False),
                Recommendation.units > 0,
            )
            .order_by(desc(Recommendation.score), desc(Recommendation.expected_value), desc(Recommendation.edge))
        ).all()
        selected_games: set[str] = set()
        total_units = 0.0
        created = 0
        max_picks = min(policy.max_official_picks, settings.max_official_picks)
        for candidate in candidates:
            if candidate.game_id in selected_games:
                continue
            if total_units + candidate.units > policy.max_daily_units:
                continue
            candidate.is_official = True
            selected_games.add(candidate.game_id)
            total_units += candidate.units
            created += 1
            if created >= max_picks:
                break
        db.commit()
        return created

    def _demo_events(self, schedule: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
        upcoming = []
        for item in schedule:
            if not item.get("game_date") or not item.get("away_team") or not item.get("home_team"):
                continue
            commence = datetime.fromisoformat(item["game_date"].replace("Z", "+00:00"))
            if commence > now:
                upcoming.append(item)
        events = []
        for index, item in enumerate(upcoming[:4]):
            away = canonical_team(item["away_team"])
            home = canonical_team(item["home_team"])
            commence = item["game_date"]
            home_price = -118 + index * 7
            away_price = 105 - index * 4
            total = 8.0 + 0.5 * (index % 3)
            event = {
                "id": f"demo-{item.get('game_pk', index)}",
                "commence_time": commence,
                "away_team": away,
                "home_team": home,
                "bookmakers": [],
            }
            for book in ("fanduel", "draftkings"):
                shift = 3 if book == "fanduel" else 0
                event["bookmakers"].append(
                    {
                        "key": book,
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": away, "price": away_price + shift},
                                    {"name": home, "price": home_price + shift},
                                ],
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": away, "price": -110 + shift, "point": 1.5},
                                    {"name": home, "price": -110, "point": -1.5},
                                ],
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -108 + shift, "point": total},
                                    {"name": "Under", "price": -112, "point": total},
                                ],
                            },
                        ],
                    }
                )
            events.append(event)
        return events
