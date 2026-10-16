"""Génère les fixtures SYNTHÉTIQUES (formes réalistes de l'API, valeurs inventées).

Ces marchés n'existent pas tels quels sur Polymarket. Ils servent aux tests, à la CI et à
l'apprentissage hors ligne. Reproductible : `uv run python tests/fixtures/generate.py`.
"""

from __future__ import annotations

import json
import math
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent
AS_OF = datetime(2026, 10, 13, tzinfo=UTC)
rng = random.Random(42)  # noqa: S311 (données de test, pas de cryptographie)


def market(
    mid, slug, question, yes, *, bid, ask, liq, vol, vol24, d1, w1, end, active=True, closed=False
):
    return {
        "id": mid,
        "slug": slug,
        "question": question,
        "conditionId": "0x" + f"{int(mid):064x}",
        "description": "Données synthétiques polysignals (fixture de test).",
        "resolutionSource": "https://example.org/source-officielle",
        "endDate": end,
        "outcomes": json.dumps(["Yes", "No"]),
        "outcomePrices": json.dumps([f"{yes:.3f}", f"{1 - yes:.3f}"]),
        "clobTokenIds": json.dumps([f"{mid}1", f"{mid}2"]),
        "active": active,
        "closed": closed,
        "bestBid": bid,
        "bestAsk": ask,
        "spread": round(ask - bid, 3),
        "lastTradePrice": yes,
        "liquidity": f"{liq:.2f}",
        "liquidityNum": liq,
        "volume": f"{vol:.2f}",
        "volumeNum": vol,
        "volume24hr": vol24,
        "oneDayPriceChange": d1,
        "oneWeekPriceChange": w1,
        "negRisk": False,
        "updatedAt": AS_OF.isoformat(),
    }


def tag(i, slug, label):
    return {"id": str(i), "slug": slug, "label": label}


EVENTS = [
    {
        "id": "9001",
        "slug": "fed-decision-december-2026",
        "title": "Décision de la Fed en décembre 2026 ?",
        "endDate": "2026-12-16T19:00:00Z",
        "active": True,
        "closed": False,
        "tags": [tag(100, "fed-rates", "Fed Rates"), tag(1, "economy", "Economy")],
        "markets": [
            market(
                "90011",
                "fed-cut-25-dec-2026",
                "La Fed baisse-t-elle ses taux de 25 pb ?",
                0.62,
                bid=0.61,
                ask=0.63,
                liq=420_000,
                vol=8_900_000,
                vol24=310_000,
                d1=0.02,
                w1=0.07,
                end="2026-12-16T19:00:00Z",
            ),
            market(
                "90012",
                "fed-no-change-dec-2026",
                "La Fed laisse-t-elle ses taux inchangés ?",
                0.33,
                bid=0.32,
                ask=0.34,
                liq=380_000,
                vol=6_100_000,
                vol24=250_000,
                d1=-0.02,
                w1=-0.06,
                end="2026-12-16T19:00:00Z",
            ),
            market(
                "90013",
                "fed-cut-50-dec-2026",
                "La Fed baisse-t-elle ses taux de 50 pb ou plus ?",
                0.04,
                bid=0.035,
                ask=0.045,
                liq=95_000,
                vol=1_200_000,
                vol24=18_000,
                d1=0.0,
                w1=-0.01,
                end="2026-12-16T19:00:00Z",
            ),
        ],
    },
    {
        "id": "9002",
        "slug": "ecb-cut-december-2026",
        "title": "La BCE baisse-t-elle ses taux en décembre 2026 ?",
        "endDate": "2026-12-17T13:15:00Z",
        "active": True,
        "closed": False,
        "tags": [tag(200, "ecb", "ECB"), tag(1, "economy", "Economy")],
        "markets": [
            market(
                "90021",
                "ecb-cut-december-2026",
                "La BCE baisse-t-elle ses taux en décembre ?",
                0.41,
                bid=0.30,
                ask=0.52,
                liq=3_200,
                vol=41_000,
                vol24=600,
                d1=0.11,
                w1=0.15,
                end="2026-12-17T13:15:00Z",
            ),
        ],
    },
    {
        "id": "9003",
        "slug": "us-cpi-above-3-november-2026",
        "title": "Inflation américaine (CPI) au-dessus de 3 % en novembre 2026 ?",
        "endDate": "2026-12-10T13:30:00Z",
        "active": True,
        "closed": False,
        "tags": [tag(300, "inflation", "Inflation"), tag(1, "economy", "Economy")],
        "markets": [
            market(
                "90031",
                "us-cpi-above-3-nov-2026",
                "Le CPI américain dépasse-t-il 3 % sur un an ?",
                0.27,
                bid=0.26,
                ask=0.28,
                liq=64_000,
                vol=930_000,
                vol24=21_000,
                d1=-0.01,
                w1=-0.04,
                end="2026-12-10T13:30:00Z",
            ),
        ],
    },
    {
        "id": "9004",
        "slug": "us-recession-2026",
        "title": "Récession aux États-Unis en 2026 ?",
        "endDate": "2027-02-28T00:00:00Z",
        "active": True,
        "closed": False,
        "tags": [tag(400, "recession", "Recession"), tag(1, "economy", "Economy")],
        "markets": [
            market(
                "90041",
                "us-recession-2026",
                "Les États-Unis entrent-ils en récession en 2026 ?",
                0.14,
                bid=0.135,
                ask=0.145,
                liq=510_000,
                vol=12_400_000,
                vol24=140_000,
                d1=-0.005,
                w1=-0.02,
                end="2027-02-28T00:00:00Z",
            ),
        ],
    },
    {
        "id": "9005",
        "slug": "us-recession-2025",
        "title": "Récession aux États-Unis en 2025 ?",
        "endDate": "2026-02-28T00:00:00Z",
        "active": False,
        "closed": True,
        "tags": [tag(400, "recession", "Recession")],
        "markets": [
            market(
                "90051",
                "us-recession-2025",
                "Les États-Unis entrent-ils en récession en 2025 ?",
                0.0,
                bid=0.0,
                ask=0.001,
                liq=0,
                vol=15_000_000,
                vol24=0,
                d1=0.0,
                w1=0.0,
                end="2026-02-28T00:00:00Z",
                active=False,
                closed=True,
            ),
        ],
    },
]


def history(final: float, days: int = 90, vol: float = 0.05) -> list[dict[str, float]]:
    """Marche aléatoire en log-odds qui se termine exactement sur `final`."""
    logit = math.log(final / (1 - final))
    steps = [rng.gauss(0, vol) for _ in range(days)]
    points, x = [], logit - sum(steps)
    for i, step in enumerate(steps):
        x += step
        t = AS_OF - timedelta(days=days - 1 - i)
        points.append({"t": int(t.timestamp()), "p": round(1 / (1 + math.exp(-x)), 4)})
    return points


def main() -> None:
    (HERE / "gamma_events.json").write_text(json.dumps(EVENTS, indent=1, ensure_ascii=False))
    histories = {}
    for event in EVENTS:
        for m in event["markets"]:
            if m["active"]:
                yes_token = json.loads(m["clobTokenIds"])[0]
                histories[yes_token] = {"history": history(m["lastTradePrice"])}
    (HERE / "clob_prices_history.json").write_text(json.dumps(histories, indent=1))


if __name__ == "__main__":
    main()
