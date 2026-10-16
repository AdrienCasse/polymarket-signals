"""Pipeline complet hors ligne : ingestion fixtures → dbt build (tous les tests dbt) → mart lu."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from polysignals import explain as ex
from polysignals.config import PROJECT_ROOT, Settings
from polysignals.ingest import run_ingestion
from polysignals.sources import FixtureSource


@pytest.mark.e2e
def test_fixtures_pipeline_builds_and_passes_dbt_tests(settings: Settings, tmp_path: Path) -> None:
    run_ingestion(settings, FixtureSource(settings.fixtures_dir))

    env = {
        **os.environ,
        "POLYSIGNALS_DATA_DIR": str(settings.data_dir),
        "DBT_LOG_PATH": str(tmp_path / "logs"),
        "DBT_TARGET_PATH": str(tmp_path / "target"),
    }
    result = subprocess.run(
        ["dbt", "build", "--profiles-dir", ".", "--warn-error-options", '{"include": []}'],
        cwd=PROJECT_ROOT / "transform",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-3000:]

    markets = ex.load_watchlist(settings.warehouse_path)
    by_slug = {m.market_slug: m for m in markets}
    assert len(markets) == 6  # le marché clos n'apparaît pas
    assert by_slug["ecb-cut-december-2026"].signal_quality == "inexploitable"
    assert by_slug["ecb-cut-december-2026"].implied_probability == pytest.approx(0.41)
    assert by_slug["fed-cut-25-dec-2026"].signal_quality == "solide"
    assert by_slug["fed-cut-25-dec-2026"].implied_probability == pytest.approx(0.62)
