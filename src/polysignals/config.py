"""Configuration centralisée.

Tout se règle par variables d'environnement préfixées `POLYSIGNALS_` (ou un fichier `.env`).
Aucun secret n'est nécessaire : les API lues sont publiques et le projet est en lecture seule.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class SourceMode(StrEnum):
    LIVE = "live"  # API publiques Polymarket
    FIXTURES = "fixtures"  # données synthétiques versionnées (tests, CI, hors ligne)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="POLYSIGNALS_", env_file=".env", extra="ignore", frozen=True
    )

    source: SourceMode = SourceMode.FIXTURES
    data_dir: Path = PROJECT_ROOT / "data"
    # Source unique de la watchlist, partagée avec dbt (seed)
    watchlist_path: Path = PROJECT_ROOT / "transform" / "seeds" / "watchlist_selectors.csv"
    fixtures_dir: Path = PROJECT_ROOT / "tests" / "fixtures"

    gamma_base_url: str = "https://gamma-api.polymarket.com"
    clob_base_url: str = "https://clob.polymarket.com"

    # Garde-fous réseau
    timeout_s: float = Field(default=15.0, gt=0, le=60)
    max_retries: int = Field(default=4, ge=0, le=8)
    min_interval_s: float = Field(default=0.25, ge=0)  # ≈ 4 requêtes/s max
    max_response_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_pages: int = Field(default=5, ge=1, le=200)
    page_size: int = Field(default=100, ge=1, le=500)

    # Historique de prix CLOB
    # 1 mois glissant par appel : l'historique long se reconstitue par accumulation des runs
    # quotidiens (dédupliqués en silver), ce qui garde la couche bronze légère
    history_interval: str = "1m"
    history_fidelity_min: int = Field(default=1440, ge=1)  # 1 point par jour
    max_history_tokens: int = Field(default=100, ge=0)  # borne le nombre d'appels CLOB par run

    @property
    def bronze_dir(self) -> Path:
        return self.data_dir / "bronze"

    @property
    def warehouse_path(self) -> Path:
        return self.data_dir / "warehouse.duckdb"


def get_settings() -> Settings:
    return Settings()
