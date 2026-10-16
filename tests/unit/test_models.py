from __future__ import annotations

import json
from pathlib import Path

from polysignals.models import ClobPriceHistory, GammaEvent, GammaMarket, check_contract

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_fixture_events_respect_contract() -> None:
    for event in json.loads((FIXTURES / "gamma_events.json").read_text()):
        assert check_contract(GammaEvent, event) == []


def test_json_encoded_lists_are_decoded() -> None:
    event = json.loads((FIXTURES / "gamma_events.json").read_text())[0]
    market = GammaMarket.model_validate(event["markets"][0])
    assert market.outcomes == ["Yes", "No"]
    assert abs(sum(market.outcome_prices) - 1) < 1e-9


def test_violation_is_reported_not_raised() -> None:
    event = json.loads((FIXTURES / "gamma_events.json").read_text())[0]
    event["markets"][0]["outcomePrices"] = '["1.7", "-0.7"]'
    del event["title"]
    errors = check_contract(GammaEvent, event)
    assert any("title" in e for e in errors)
    assert any("outcome_prices" in e or "outcomePrices" in e for e in errors)


def test_unknown_fields_are_allowed() -> None:
    assert check_contract(ClobPriceHistory, {"history": [], "nouveau_champ": 1}) == []


def test_price_out_of_range_is_a_violation() -> None:
    assert check_contract(ClobPriceHistory, {"history": [{"t": 1, "p": 1.2}]})
