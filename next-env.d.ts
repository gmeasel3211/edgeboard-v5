from app.services.model import ModelEngine
from app.services.settings_service import ModelPolicy


def test_candidate_evaluation_positive_edge() -> None:
    result = ModelEngine(1000).evaluate_candidate(
        model_probability=0.58,
        market_probability=0.52,
        odds=-105,
        confidence=0.80,
        data_quality=80,
        policy=ModelPolicy(),
    )
    assert result["edge"] > 0
    assert result["expected_value"] > 0
    assert result["fair_odds"] < 0
