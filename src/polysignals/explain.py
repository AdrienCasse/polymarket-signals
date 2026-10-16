"""Explication pédagogique d'un marché, à partir de la couche gold.

Fonctions pures (pas d'affichage) : elles renvoient du texte, ce qui les rend testables.
La mise en forme (couleurs, panneaux) est faite par la CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import duckdb

SPARK_CHARS = "▁▂▃▄▅▆▇█"

PASSIVE_INVESTOR_NOTE = (
    "Ce signal n'appelle aucune action sur ton épargne : une stratégie passive (épargne de "
    "précaution, livrets, PEA en DCA) ne se pilote pas sur des probabilités de court terme. "
    "Il sert à comprendre le contexte, par exemple pourquoi les marchés bougent ou pourquoi le "
    "taux du Livret A pourrait changer."
)


@dataclass(frozen=True)
class MarketView:
    market_id: str
    theme_id: str
    theme_label: str
    event_title: str
    question: str
    market_slug: str
    implied_probability: float
    change_7d: float | None
    change_30d: float | None
    min_90d: float | None
    max_90d: float | None
    best_bid: float | None
    best_ask: float | None
    spread: float | None
    last_trade_price: float | None
    liquidity_usd: float | None
    volume_24h_usd: float | None
    end_at: datetime | None
    days_to_resolution: int | None
    signal_quality: str
    quality_reasons: list[str]
    resolution_source: str | None
    why_it_matters: str
    academy_lesson: str
    as_of: datetime


class WarehouseNotBuiltError(RuntimeError):
    pass


def _connect(warehouse: Path) -> duckdb.DuckDBPyConnection:
    if not warehouse.exists():
        raise WarehouseNotBuiltError(
            "Entrepôt absent : lance `make pipeline` (ou `make demo` hors ligne)."
        )
    return duckdb.connect(str(warehouse), read_only=True, config={"TimeZone": "UTC"})


def load_watchlist(warehouse: Path) -> list[MarketView]:
    with _connect(warehouse) as con:
        cur = con.execute(
            "select * from gold.mart_macro_watchlist "
            "order by theme_id, liquidity_usd desc nulls last"
        )
        return _rows(cur)


def find_market(warehouse: Path, ref: str) -> MarketView | None:
    with _connect(warehouse) as con:
        cur = con.execute(
            "select * from gold.mart_macro_watchlist "
            "where market_id = $ref or market_slug = $ref limit 1",
            {"ref": ref},
        )
        rows = _rows(cur)
    return rows[0] if rows else None


def price_series(warehouse: Path, market_id: str, days: int = 90) -> list[tuple[date, float]]:
    with _connect(warehouse) as con:
        rows = con.execute(
            "select price_date, close_probability from gold.fct_daily_prices "
            "where market_id = $id order by price_date desc limit $n",
            {"id": market_id, "n": days},
        ).fetchall()
    return [(r[0], r[1]) for r in reversed(rows)]


def _rows(cur: duckdb.DuckDBPyConnection) -> list[MarketView]:
    cols = [d[0] for d in cur.description or []]
    fields = MarketView.__dataclass_fields__
    return [
        MarketView(**{k: v for k, v in zip(cols, row, strict=True) if k in fields})
        for row in cur.fetchall()
    ]


# ── Mise en mots ──────────────────────────────────────────────────────────────


def pct(p: float | None) -> str:
    return "n/d" if p is None else f"{p * 100:.0f} %"


def pts(delta: float | None) -> str:
    if delta is None:
        return "n/d"
    return f"{delta * 100:+.1f} pts"


def usd(x: float | None) -> str:
    return "n/d" if x is None else f"{x:,.0f} $".replace(",", " ")


def sparkline(values: list[float], width: int = 45) -> str:
    if not values:
        return ""
    step = max(1, -(-len(values) // width))  # division arrondie au supérieur
    values = values[::-1][::step][::-1]  # échantillonne en gardant le dernier point
    lo, hi = min(values), max(values)
    span = hi - lo or 1.0
    return "".join(SPARK_CHARS[round((v - lo) / span * (len(SPARK_CHARS) - 1))] for v in values)


def what_market_says(m: MarketView) -> list[str]:
    p = m.implied_probability
    lines = [
        f"Les participants estiment à {pct(p)} la probabilité que la réponse soit « Oui ».",
        f"Concrètement, une part « Oui » coûte {p:.2f} $ et rapporte 1 $ si l'événement se "
        f"produit, 0 $ sinon. Le prix EST la probabilité implicite.",
    ]
    if m.best_bid is not None and m.best_ask is not None and m.spread is not None:
        how = (
            "écart serré → on retient le point milieu"
            if m.spread <= 0.10
            else "écart trop large → on retient le dernier prix échangé"
        )
        lines.append(
            f"Carnet d'ordres : meilleur acheteur {m.best_bid:.3f} $, meilleur vendeur "
            f"{m.best_ask:.3f} $, écart {m.spread * 100:.1f} pts ({how})."
        )
    else:
        lines.append("Carnet d'ordres vide : on retient le dernier prix échangé.")
    return lines


def how_it_moved(m: MarketView, series: list[tuple[date, float]]) -> list[str]:
    lines = [f"Sur 7 jours : {pts(m.change_7d)}   ·   sur 30 jours : {pts(m.change_30d)}"]
    if m.min_90d is not None and m.max_90d is not None:
        lines.append(f"Fourchette sur 90 jours : {pct(m.min_90d)} → {pct(m.max_90d)}")
    if series:
        lines.append(
            f"{series[0][0]:%d/%m}  {sparkline([v for _, v in series])}  {series[-1][0]:%d/%m}"
        )
    if m.change_7d is not None and abs(m.change_7d) < 0.03:
        lines.append(
            "Une variation de moins de 3 points relève souvent du bruit, pas d'une information."
        )
    return lines


def can_we_trust_it(m: MarketView) -> list[str]:
    verdict = {
        "solide": "Signal SOLIDE : carnet profond, écart serré, prix difficile à déplacer.",
        "fragile": "Signal FRAGILE : à lire avec prudence.",
        "inexploitable": "Signal INEXPLOITABLE : le prix affiché ne mesure pas grand-chose.",
    }[m.signal_quality]
    lines = [verdict, *(f"  · {r}" for r in m.quality_reasons)]
    lines.append(f"Liquidité : {usd(m.liquidity_usd)}   ·   volume 24 h : {usd(m.volume_24h_usd)}")
    if m.days_to_resolution is not None:
        lines.append(f"Résolution dans {m.days_to_resolution} jours ({m.end_at:%d/%m/%Y}).")
    if m.resolution_source:
        lines.append(f"Source de résolution : {m.resolution_source}")
    lines.append(
        "Rappel : un marché prédictif agrège des paris, pas des prévisions d'experts. "
        "Il peut se tromper, et les petits marchés se manipulent facilement."
    )
    return lines


def what_it_means_for_you(m: MarketView) -> list[str]:
    return [
        m.why_it_matters,
        PASSIVE_INVESTOR_NOTE,
        f"Pour aller plus loin : academy/{m.academy_lesson}.md",
    ]


def to_dict(m: MarketView) -> dict[str, Any]:
    return {k: getattr(m, k) for k in MarketView.__dataclass_fields__}
