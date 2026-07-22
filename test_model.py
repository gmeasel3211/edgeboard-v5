from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy.orm import Session

from ..models import AppSetting


@dataclass
class ModelPolicy:
    bankroll: float = 1000.0
    unit_percent: float = 0.01
    kelly_fraction: float = 0.25
    max_bet_units: float = 2.0
    max_daily_units: float = 5.0
    min_edge: float = 0.025
    min_ev: float = 0.025
    min_data_quality: int = 60
    min_score: float = 64.0
    max_model_market_disagreement: float = 0.16
    max_official_picks: int = 3


ALLOWED_SETTINGS: dict[str, tuple[type, float | int, float | int]] = {
    "bankroll": (float, 10.0, 10_000_000.0),
    "unit_percent": (float, 0.001, 0.05),
    "kelly_fraction": (float, 0.0, 1.0),
    "max_bet_units": (float, 0.1, 10.0),
    "max_daily_units": (float, 0.5, 50.0),
    "min_edge": (float, 0.0, 0.25),
    "min_ev": (float, 0.0, 0.50),
    "min_data_quality": (int, 0, 100),
    "min_score": (float, 0.0, 100.0),
    "max_model_market_disagreement": (float, 0.01, 0.50),
    "max_official_picks": (int, 1, 20),
}


def get_policy(db: Session) -> ModelPolicy:
    defaults = asdict(ModelPolicy())
    rows = db.query(AppSetting).filter(AppSetting.key.in_(list(defaults))).all()
    for row in rows:
        defaults[row.key] = row.value_json
    return ModelPolicy(**defaults)


def update_policy(db: Session, values: dict[str, Any], user_id: str | None) -> ModelPolicy:
    for key, raw_value in values.items():
        if key not in ALLOWED_SETTINGS:
            raise ValueError(f"Unsupported setting: {key}")
        expected_type, low, high = ALLOWED_SETTINGS[key]
        value = expected_type(raw_value)
        if not low <= value <= high:
            raise ValueError(f"{key} must be between {low} and {high}")
        row = db.get(AppSetting, key)
        if row is None:
            row = AppSetting(key=key, value_json=value, updated_by_user_id=user_id)
            db.add(row)
        else:
            row.value_json = value
            row.updated_by_user_id = user_id
    db.commit()
    return get_policy(db)
