from __future__ import annotations

from datetime import UTC, datetime

from polysignals import explain as ex


def _market(**overrides: object) -> ex.MarketView:
    base: dict[str, object] = dict(
        market_id="1",
        theme_id="fed",
        theme_label="Fed",
        event_title="E",
        question="Q ?",
        market_slug="q",
        implied_probability=0.62,
        change_7d=0.01,
        change_30d=-0.05,
        min_90d=0.5,
        max_90d=0.7,
        best_bid=0.61,
        best_ask=0.63,
        spread=0.02,
        last_trade_price=0.6,
        liquidity_usd=420_000.0,
        volume_24h_usd=1_000.0,
        end_at=datetime(2026, 12, 16, tzinfo=UTC),
        days_to_resolution=63,
        signal_quality="solide",
        quality_reasons=[],
        resolution_source=None,
        why_it_matters="Parce que.",
        academy_lesson="05-lire-un-signal-macro",
        as_of=datetime(2026, 10, 14, tzinfo=UTC),
    )
    base.update(overrides)
    return ex.MarketView(**base)  # type: ignore[arg-type]


def test_price_is_explained_as_probability() -> None:
    text = "\n".join(ex.what_market_says(_market()))
    assert "62 %" in text and "point milieu" in text


def test_wide_spread_explains_last_trade_rule() -> None:
    text = "\n".join(ex.what_market_says(_market(spread=0.22, best_bid=0.3, best_ask=0.52)))
    assert "dernier prix échangé" in text


def test_small_moves_are_flagged_as_noise() -> None:
    assert any("bruit" in line for line in ex.how_it_moved(_market(change_7d=0.01), []))
    assert not any("bruit" in line for line in ex.how_it_moved(_market(change_7d=0.08), []))


def test_passive_investor_note_is_always_present() -> None:
    assert ex.PASSIVE_INVESTOR_NOTE in ex.what_it_means_for_you(_market())


def test_sparkline_is_bounded() -> None:
    assert len(ex.sparkline([float(i) for i in range(200)], width=40)) <= 40
    assert ex.sparkline([]) == ""
    assert ex.sparkline([0.5, 0.5]) == "▁▁"


def test_formatting() -> None:
    assert ex.pts(0.034) == "+3.4 pts"
    assert ex.pct(None) == "n/d"
