"""Orchestration de l'ingestion : watchlist → source → contrat → bronze.

1. lire la watchlist (seed dbt `watchlist_selectors.csv`, source unique de vérité)
2. pour chaque sélecteur, récupérer les événements ouverts et leurs marchés (Gamma)
3. pour chaque marché binaire actif, récupérer l'historique de prix de l'issue « Yes » (CLOB)
4. valider chaque enregistrement contre son contrat, l'écrire en bronze (idempotent)
5. écrire le manifeste du run (compteurs, statut) : base des contrôles de fraîcheur
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from polysignals.bronze import BronzeWriter, RunManifest, new_run_id, write_manifest
from polysignals.config import Settings
from polysignals.models import ClobPriceHistory, GammaEvent, GammaMarket, check_contract
from polysignals.sources import Source

log = logging.getLogger(__name__)

SELECTOR_PARAMS = {"tag": "tag_slug", "event": "slug"}


@dataclass(frozen=True)
class Selector:
    theme_id: str
    selector_type: str
    selector_value: str

    def gamma_params(self) -> dict[str, str]:
        return {SELECTOR_PARAMS[self.selector_type]: self.selector_value, "closed": "false"}


def load_watchlist(path: Path) -> list[Selector]:
    with path.open(newline="") as fh:
        rows = [Selector(**row) for row in csv.DictReader(fh)]
    unknown = {r.selector_type for r in rows} - SELECTOR_PARAMS.keys()
    if unknown:
        raise ValueError(f"selector_type inconnu dans {path.name} : {sorted(unknown)}")
    return rows


def run_ingestion(settings: Settings, source: Source, now: datetime | None = None) -> RunManifest:
    now = now or datetime.now(UTC)
    manifest = RunManifest(
        run_id=new_run_id(now), mode=settings.source.value, started_at=now.isoformat()
    )
    writer = BronzeWriter(settings.bronze_dir, manifest.run_id, now)
    try:
        tokens = _ingest_events(settings, source, writer, manifest)
        _ingest_price_history(settings, source, writer, manifest, tokens)
        manifest.status = "success"
    except Exception as exc:
        manifest.status = "failed"
        manifest.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        manifest.finished_at = datetime.now(UTC).isoformat()
        write_manifest(settings.bronze_dir, manifest)
    return manifest


def _ingest_events(
    settings: Settings, source: Source, writer: BronzeWriter, manifest: RunManifest
) -> list[str]:
    tokens: dict[str, float] = {}  # token « Yes » → liquidité (pour prioriser l'historique)
    for selector in load_watchlist(settings.watchlist_path):
        params = selector.gamma_params()
        for page in source.events(params):
            writer.write(
                "gamma",
                "events",
                params,
                ((str(e.get("id")), e, check_contract(GammaEvent, e)) for e in page),
                manifest,
            )
            for event in page:
                for market in event.get("markets") or []:
                    token = _yes_token(market)
                    if token:
                        tokens[token] = max(tokens.get(token, 0.0), _liquidity(market))
    log.info("%s marchés binaires actifs repérés", len(tokens))
    ranked = sorted(tokens, key=lambda t: tokens[t], reverse=True)
    return ranked[: settings.max_history_tokens]


def _ingest_price_history(
    settings: Settings,
    source: Source,
    writer: BronzeWriter,
    manifest: RunManifest,
    tokens: list[str],
) -> None:
    for token in tokens:
        params = {
            "market": token,
            "interval": settings.history_interval,
            "fidelity": settings.history_fidelity_min,
        }
        payload = source.price_history(token)
        writer.write(
            "clob",
            "prices_history",
            params,
            [(token, payload, check_contract(ClobPriceHistory, payload))],
            manifest,
        )


def _yes_token(market: dict[str, Any]) -> str | None:
    """Token de l'issue « Yes » d'un marché binaire actif, sinon None."""
    try:
        parsed = GammaMarket.model_validate(market)
    except ValueError:
        return None
    if parsed.closed or not parsed.active or parsed.outcomes != ["Yes", "No"]:
        return None
    return parsed.clob_token_ids[0] if parsed.clob_token_ids else None


def _liquidity(market: dict[str, Any]) -> float:
    try:
        return float(market.get("liquidityNum") or 0.0)
    except (TypeError, ValueError):
        return 0.0
