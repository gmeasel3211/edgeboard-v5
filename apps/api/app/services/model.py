from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Any

from .math_utils import expected_value, implied_to_american, kelly_fraction
from .settings_service import ModelPolicy


@dataclass
class ProjectionResult:
    away_runs: float
    home_runs: float
    away_win_probability: float
    home_win_probability: float
    total_mean: float
    data_quality: int
    confidence: float
    market_disagreement: float
    probabilities: dict[str, float]
    reasons: list[str]
    inputs: dict[str, Any]
    simulations: int


class ModelEngine:
    LEAGUE_RUNS = 4.50

    def __init__(self, simulations: int = 10_000) -> None:
        self.simulations = max(simulations, 1_000)

    @staticmethod
    def candidate_key(market: str, selection: str, line: float | None) -> str:
        line_text = "" if line is None else f":{line:g}"
        return f"{market}:{selection}{line_text}"

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return min(max(value, low), high)

    @staticmethod
    def _poisson(rng: random.Random, mean: float) -> int:
        threshold = math.exp(-max(mean, 0.01))
        product = 1.0
        count = 0
        while product > threshold:
            count += 1
            product *= rng.random()
        return count - 1

    def project_game(
        self,
        *,
        game_id: str,
        away_team_name: str,
        home_team_name: str,
        away_team: dict[str, Any],
        home_team: dict[str, Any],
        away_recent: dict[str, Any],
        home_recent: dict[str, Any],
        away_pitcher: dict[str, Any],
        home_pitcher: dict[str, Any],
        weather: dict[str, Any],
        park_factor: float,
        away_rest_days: int,
        home_rest_days: int,
        market_home_probability: float | None,
        candidates: list[dict[str, Any]],
    ) -> ProjectionResult:
        away_offense = 0.78 * away_team["runs_for_game"] + 0.22 * away_recent["runs_for_game"]
        home_offense = 0.78 * home_team["runs_for_game"] + 0.22 * home_recent["runs_for_game"]
        away_defense = 0.78 * away_team["runs_against_game"] + 0.22 * away_recent["runs_against_game"]
        home_defense = 0.78 * home_team["runs_against_game"] + 0.22 * home_recent["runs_against_game"]

        away_base = math.sqrt(max(away_offense, 2.0) * max(home_defense, 2.0))
        home_base = math.sqrt(max(home_offense, 2.0) * max(away_defense, 2.0))

        home_starter_factor = self._clamp(
            0.58 + 0.28 * (home_pitcher["era"] / self.LEAGUE_RUNS) + 0.10 * (home_pitcher["whip"] / 1.30),
            0.76,
            1.27,
        )
        away_starter_factor = self._clamp(
            0.58 + 0.28 * (away_pitcher["era"] / self.LEAGUE_RUNS) + 0.10 * (away_pitcher["whip"] / 1.30),
            0.76,
            1.27,
        )

        # Bullpen proxy uses team run prevention after accounting for the listed starter.
        home_bullpen_proxy = self._clamp(0.82 + 0.18 * (home_team["era"] / self.LEAGUE_RUNS), 0.88, 1.14)
        away_bullpen_proxy = self._clamp(0.82 + 0.18 * (away_team["era"] / self.LEAGUE_RUNS), 0.88, 1.14)

        environment = self._clamp(park_factor * weather["run_factor"], 0.80, 1.25)
        away_rest_factor = 0.985 if away_rest_days <= 0 else 1.0 if away_rest_days == 1 else 1.01
        home_rest_factor = 0.985 if home_rest_days <= 0 else 1.0 if home_rest_days == 1 else 1.01

        away_runs = away_base * (0.70 * home_starter_factor + 0.30 * home_bullpen_proxy) * environment
        home_runs = (
            home_base * (0.70 * away_starter_factor + 0.30 * away_bullpen_proxy) * environment + 0.12
        )
        away_runs = self._clamp(away_runs * away_rest_factor, 1.5, 8.5)
        home_runs = self._clamp(home_runs * home_rest_factor, 1.5, 8.5)

        qualities = [
            away_team["quality"],
            home_team["quality"],
            away_recent["quality"],
            home_recent["quality"],
            away_pitcher["quality"],
            home_pitcher["quality"],
            weather["quality"],
            90 if market_home_probability is not None else 35,
        ]
        data_quality = round(sum(qualities) / len(qualities))

        seed = int(hashlib.sha256(game_id.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        wins = {away_team_name: 0, home_team_name: 0}
        candidate_wins = {self.candidate_key(c["market"], c["selection"], c.get("line")): 0 for c in candidates}
        total_runs_sum = 0
        away_runs_sum = 0
        home_runs_sum = 0

        for _ in range(self.simulations):
            away_score = self._poisson(rng, away_runs)
            home_score = self._poisson(rng, home_runs)
            if away_score == home_score:
                if rng.random() < 0.535:
                    home_score += 1
                else:
                    away_score += 1
            away_runs_sum += away_score
            home_runs_sum += home_score
            total_runs_sum += away_score + home_score
            winner = home_team_name if home_score > away_score else away_team_name
            wins[winner] += 1

            for candidate in candidates:
                market = candidate["market"]
                selection = candidate["selection"]
                line = candidate.get("line")
                won = False
                if market == "h2h":
                    won = selection == winner
                elif market == "spreads" and line is not None:
                    score = away_score if selection == away_team_name else home_score
                    opponent = home_score if selection == away_team_name else away_score
                    won = score + float(line) > opponent
                elif market == "totals" and line is not None:
                    total = away_score + home_score
                    won = total > float(line) if selection.lower() == "over" else total < float(line)
                if won:
                    candidate_wins[self.candidate_key(market, selection, line)] += 1

        simulated_home = wins[home_team_name] / self.simulations
        simulated_away = wins[away_team_name] / self.simulations
        disagreement = abs(simulated_home - market_home_probability) if market_home_probability is not None else 0.0

        if market_home_probability is not None:
            market_weight = self._clamp(0.38 - (data_quality - 60) * 0.003, 0.20, 0.38)
            home_probability = (1 - market_weight) * simulated_home + market_weight * market_home_probability
        else:
            home_probability = simulated_home
        home_probability = self._clamp(home_probability, 0.12, 0.88)
        away_probability = 1 - home_probability

        probability_map = {key: value / self.simulations for key, value in candidate_wins.items()}
        probability_map[self.candidate_key("h2h", home_team_name, None)] = home_probability
        probability_map[self.candidate_key("h2h", away_team_name, None)] = away_probability

        confidence = self._clamp(
            0.55 * (data_quality / 100)
            + 0.25 * min(abs(home_probability - 0.5) / 0.18, 1)
            + 0.20 * (1 - min(disagreement / 0.15, 1)),
            0,
            1,
        )

        reasons = [
            f"Projected score: {away_team_name} {away_runs:.2f}, {home_team_name} {home_runs:.2f}.",
            f"Starting-pitcher inputs: {away_pitcher['era']:.2f}/{away_pitcher['whip']:.2f} away ERA/WHIP versus {home_pitcher['era']:.2f}/{home_pitcher['whip']:.2f} home.",
            f"Park and weather run multiplier: {environment:.3f}.",
            f"Season/recent-form blend: 78% season, 22% recent window.",
            f"Simulation sample: {self.simulations:,}; data quality {data_quality}/100.",
        ]
        if market_home_probability is not None:
            reasons.append(
                f"No-vig market anchor {market_home_probability:.1%}; model-market disagreement {disagreement:.1%}."
            )
        else:
            reasons.append("No reliable market anchor was available, so uncertainty was increased.")
        reasons.append("Bullpen impact is currently a team run-prevention proxy, not a licensed availability feed.")

        return ProjectionResult(
            away_runs=away_runs_sum / self.simulations,
            home_runs=home_runs_sum / self.simulations,
            away_win_probability=away_probability,
            home_win_probability=home_probability,
            total_mean=total_runs_sum / self.simulations,
            data_quality=data_quality,
            confidence=confidence,
            market_disagreement=disagreement,
            probabilities=probability_map,
            reasons=reasons,
            inputs={
                "away_team": away_team,
                "home_team": home_team,
                "away_recent": away_recent,
                "home_recent": home_recent,
                "away_pitcher": away_pitcher,
                "home_pitcher": home_pitcher,
                "weather": weather,
                "park_factor": park_factor,
                "away_rest_days": away_rest_days,
                "home_rest_days": home_rest_days,
                "market_home_probability": market_home_probability,
            },
            simulations=self.simulations,
        )

    def evaluate_candidate(
        self,
        *,
        model_probability: float,
        market_probability: float,
        odds: int,
        confidence: float,
        data_quality: int,
        policy: ModelPolicy,
        force: bool = False,
    ) -> dict[str, Any]:
        edge = model_probability - market_probability
        ev = expected_value(model_probability, odds)
        quality_scale = self._clamp(data_quality / 100, 0, 1)
        edge_scale = self._clamp(edge / 0.08, 0, 1)
        ev_scale = self._clamp(ev / 0.12, 0, 1)
        price_scale = 1.0 if -180 <= odds <= 160 else 0.80 if -240 <= odds <= 240 else 0.55
        score = 100 * (
            0.30 * ev_scale
            + 0.25 * edge_scale
            + 0.20 * quality_scale
            + 0.15 * confidence
            + 0.10 * price_scale
        )
        raw_kelly = kelly_fraction(model_probability, odds) * policy.kelly_fraction
        units = raw_kelly / max(policy.unit_percent, 0.001)
        units *= quality_scale * confidence * price_scale
        units = round(min(max(units, 0), policy.max_bet_units), 2)

        minimum_edge = policy.min_edge * (0.80 if force else 1.0)
        minimum_ev = policy.min_ev * (0.80 if force else 1.0)
        minimum_score = policy.min_score * (0.90 if force else 1.0)
        passes = (
            edge >= minimum_edge
            and ev >= minimum_ev
            and data_quality >= policy.min_data_quality
            and score >= minimum_score
            and -300 <= odds <= 350
            and abs(model_probability - market_probability) <= policy.max_model_market_disagreement
            and units >= 0.10
        )
        if not passes:
            units = 0.0

        if score >= 84 and ev >= 0.08 and data_quality >= 78:
            grade = "A+"
        elif score >= 76 and ev >= 0.055 and data_quality >= 72:
            grade = "A"
        elif score >= 68 and ev >= 0.035:
            grade = "B+"
        elif passes:
            grade = "B"
        else:
            grade = "Pass"

        return {
            "fair_odds": implied_to_american(model_probability),
            "edge": edge,
            "expected_value": ev,
            "score": round(score, 1),
            "units": units,
            "grade": grade,
            "passes": passes,
        }
