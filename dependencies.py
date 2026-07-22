from __future__ import annotations

import math


def american_to_implied(odds: int) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be zero")
    return 100 / (odds + 100) if odds > 0 else -odds / (-odds + 100)


def implied_to_american(probability: float) -> int:
    probability = min(max(probability, 0.001), 0.999)
    if probability >= 0.5:
        return round(-100 * probability / (1 - probability))
    return round(100 * (1 - probability) / probability)


def decimal_odds(american: int) -> float:
    return 1 + (american / 100 if american > 0 else 100 / abs(american))


def expected_value(probability: float, american: int) -> float:
    profit = american / 100 if american > 0 else 100 / abs(american)
    return probability * profit - (1 - probability)


def kelly_fraction(probability: float, american: int) -> float:
    b = american / 100 if american > 0 else 100 / abs(american)
    q = 1 - probability
    return max((b * probability - q) / b, 0.0)


def no_vig_probabilities(implied: list[float]) -> list[float]:
    total = sum(implied)
    return [value / total for value in implied] if total else implied


def profit_for_units(units: float, american: int) -> float:
    return units * (american / 100 if american > 0 else 100 / abs(american))
