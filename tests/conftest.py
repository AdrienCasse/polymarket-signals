from __future__ import annotations

from pathlib import Path

import pytest

from polysignals.config import PROJECT_ROOT, Settings, SourceMode


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Réglages isolés : données dans un dossier temporaire, aucune attente réseau."""
    return Settings(
        source=SourceMode.FIXTURES,
        data_dir=tmp_path / "data",
        fixtures_dir=PROJECT_ROOT / "tests" / "fixtures",
        min_interval_s=0,
        max_retries=2,
    )
