"""L'export est la porte de sortie vers le site public : il doit refuser tout ce qui est douteux."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from polysignals.export import ExportError, _test_summary, write_export


def _payload(markets: int = 1, tests: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "markets": [{"market_id": str(i)} for i in range(markets)],
        "tests": tests,
    }


def test_refuses_empty_site(tmp_path: Path) -> None:
    with pytest.raises(ExportError, match="site vide"):
        write_export(_payload(markets=0), tmp_path / "gold.json", min_markets=1)
    assert not (tmp_path / "gold.json").exists()


def test_refuses_when_dbt_tests_failed(tmp_path: Path) -> None:
    with pytest.raises(ExportError, match="tests dbt"):
        write_export(_payload(tests={"error": 0, "fail": 2}), tmp_path / "gold.json", 1)


def test_writes_atomically(tmp_path: Path) -> None:
    out = tmp_path / "sub" / "gold.json"
    write_export(_payload(tests={"error": 0, "fail": 0}), out, 1)
    assert json.loads(out.read_text())["schema_version"] == 1
    assert not out.with_suffix(".tmp").exists()


def test_summarises_dbt_run_results(tmp_path: Path) -> None:
    rr = tmp_path / "run_results.json"
    rr.write_text(
        json.dumps(
            {
                "metadata": {"generated_at": "2026-10-15T05:20:00Z"},
                "results": [
                    {"unique_id": "model.p.a", "status": "success"},
                    {"unique_id": "test.p.b", "status": "pass"},
                    {"unique_id": "test.p.c", "status": "warn"},
                    {"unique_id": "unit_test.p.d", "status": "fail"},
                ],
            }
        )
    )
    summary = _test_summary(rr)
    assert summary is not None
    assert (summary["tests"], summary["pass"], summary["warn"], summary["fail"]) == (3, 1, 1, 1)
    assert _test_summary(tmp_path / "absent.json") is None
