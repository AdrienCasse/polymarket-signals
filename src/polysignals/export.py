"""Export de la couche gold vers un fichier JSON unique, lu au build par le site web.

Le site est 100 % statique : pas d'API, pas de base exposée. Ce fichier est son **seul**
contrat avec le pipeline (`schema_version`). Il n'est produit que si `dbt build` a réussi :
un site ne publie jamais une donnée qui n'a pas passé les tests.
"""

from __future__ import annotations

import json
import math
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import duckdb

from polysignals.explain import WarehouseNotBuiltError

SCHEMA_VERSION = 1
SERIES_DAYS = 90
RUNS_KEPT = 30


class ExportError(RuntimeError):
    pass


def build_export(warehouse: Path, bronze_dir: Path, run_results: Path | None) -> dict[str, Any]:
    if not warehouse.exists():
        raise WarehouseNotBuiltError("Entrepôt absent : lance `make build` d'abord.")
    with duckdb.connect(str(warehouse), read_only=True, config={"TimeZone": "UTC"}) as con:
        markets = _records(
            con, "select * from gold.mart_macro_watchlist order by theme_id, liquidity_usd desc"
        )
        themes = _records(con, "select * from ref.themes order by theme_id")
        series_rows = con.execute(
            """
            select market_id, price_date, close_probability
            from gold.fct_daily_prices
            qualify row_number() over (partition by market_id order by price_date desc) <= $n
            order by market_id, price_date
            """,
            {"n": SERIES_DAYS},
        ).fetchall()

    series: dict[str, list[list[Any]]] = {}
    for market_id, day, p in series_rows:
        series.setdefault(market_id, []).append([day.isoformat(), round(p, 4)])
    for m in markets:
        m["series"] = series.get(m["market_id"], [])

    runs = _runs(bronze_dir)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "source_mode": runs[0]["mode"] if runs else None,
        "runs": runs,
        "tests": _test_summary(run_results),
        "themes": themes,
        "markets": markets,
    }


def write_export(payload: dict[str, Any], out: Path, min_markets: int) -> None:
    if len(payload["markets"]) < min_markets:
        raise ExportError(
            f"{len(payload['markets'])} marché(s) seulement (minimum {min_markets}) : "
            "export refusé pour ne pas publier un site vide."
        )
    tests = payload["tests"]
    if tests and (tests["error"] or tests["fail"]):
        raise ExportError("Des tests dbt ont échoué : export refusé.")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=_json))
    tmp.replace(out)


def _records(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description or []]
    return [
        {c: round(v, 4) if isinstance(v, float) else v for c, v in zip(cols, row, strict=True)}
        for row in cur.fetchall()
    ]


def _runs(bronze_dir: Path) -> list[dict[str, Any]]:
    files = sorted(bronze_dir.glob("_runs/*.json"), reverse=True)[:RUNS_KEPT]
    runs = []
    for f in files:
        r = json.loads(f.read_text())
        runs.append(
            {
                "run_id": r["run_id"],
                "mode": r["mode"],
                "status": r["status"],
                "started_at": r["started_at"],
                "finished_at": r.get("finished_at"),
                "written": sum(c.get("written", 0) for c in r["counts"].values()),
                "skipped": sum(c.get("skipped", 0) for c in r["counts"].values()),
            }
        )
    return runs


def _test_summary(run_results: Path | None) -> dict[str, Any] | None:
    """Résumé de `transform/target/run_results.json` (dernier `dbt build`)."""
    if run_results is None or not run_results.exists():
        return None
    data = json.loads(run_results.read_text())
    counts = {"pass": 0, "warn": 0, "error": 0, "fail": 0, "skipped": 0, "success": 0}
    tests = 0
    for r in data.get("results", []):
        uid: str = r.get("unique_id", "")
        if uid.startswith(("test.", "unit_test.")):
            tests += 1
        status = r.get("status")
        if status in counts:
            counts[status] += 1
    return {
        "generated_at": data.get("metadata", {}).get("generated_at"),
        "tests": tests,
        "nodes": len(data.get("results", [])),
        **counts,
    }


def _json(value: Any) -> Any:
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    raise TypeError(f"Type non sérialisable : {type(value).__name__}")
