"""Sources de données : API publiques Polymarket (live) ou fixtures synthétiques (hors ligne).

Les deux implémentent le même protocole : le reste du pipeline ignore d'où viennent les données.
C'est ce qui permet de tester et de faire tourner la CI sans réseau.

API utilisées (publiques, sans authentification, lecture seule) :
- Gamma  `GET /events`          événements et leurs marchés (questions, prix, liquidité)
- Gamma  `GET /tags`            liste des thèmes (pour choisir les sélecteurs de la watchlist)
- CLOB   `GET /prices-history`  historique du prix d'une issue (token)
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Protocol

from polysignals.config import Settings, SourceMode
from polysignals.http import ReadOnlyClient


class Source(Protocol):
    def events(self, params: dict[str, Any]) -> Iterator[list[dict[str, Any]]]:
        """Pages d'événements correspondant aux filtres Gamma `params`."""
        ...

    def price_history(self, token_id: str) -> dict[str, Any]: ...

    def tags(self) -> list[dict[str, Any]]: ...


class LiveSource:
    def __init__(self, settings: Settings, client: ReadOnlyClient) -> None:
        self._s = settings
        self._client = client

    def events(self, params: dict[str, Any]) -> Iterator[list[dict[str, Any]]]:
        for page in range(self._s.max_pages):
            batch = self._client.get_json(
                f"{self._s.gamma_base_url}/events",
                {**params, "limit": self._s.page_size, "offset": page * self._s.page_size},
            )
            if not isinstance(batch, list):
                raise ValueError("Gamma /events doit renvoyer une liste")
            # Défense en profondeur : si l'API ignorait un filtre, on ne garde que ce qui a été
            # demandé (sinon une watchlist « fed » ingérerait tout Polymarket)
            kept = [e for e in batch if _matches(e, params)]
            if kept:
                yield kept
            if len(batch) < self._s.page_size:
                return

    def price_history(self, token_id: str) -> dict[str, Any]:
        data = self._client.get_json(
            f"{self._s.clob_base_url}/prices-history",
            {
                "market": token_id,
                "interval": self._s.history_interval,
                "fidelity": self._s.history_fidelity_min,
            },
        )
        if not isinstance(data, dict):
            raise ValueError("CLOB /prices-history doit renvoyer un objet")
        return data

    def tags(self) -> list[dict[str, Any]]:
        data = self._client.get_json(f"{self._s.gamma_base_url}/tags", {"limit": 1000})
        return data if isinstance(data, list) else []


def _matches(event: dict[str, Any], params: dict[str, Any]) -> bool:
    if "tag_slug" in params:
        tags = event.get("tags") or []
        return any(isinstance(t, dict) and t.get("slug") == params["tag_slug"] for t in tags)
    if "slug" in params:
        return bool(event.get("slug") == params["slug"])
    return True


class FixtureSource:
    """Lit `tests/fixtures/`. Données SYNTHÉTIQUES : formes réalistes, valeurs inventées."""

    def __init__(self, fixtures_dir: Path) -> None:
        self._dir = fixtures_dir

    def events(self, params: dict[str, Any]) -> Iterator[list[dict[str, Any]]]:
        events: list[dict[str, Any]] = self._load("gamma_events.json")
        if "tag_slug" in params:
            selected = [
                e for e in events if any(t["slug"] == params["tag_slug"] for t in e["tags"])
            ]
        elif "slug" in params:
            selected = [e for e in events if e["slug"] == params["slug"]]
        else:
            selected = events
        if params.get("closed") == "false":
            selected = [e for e in selected if not e["closed"]]
        if selected:
            yield selected

    def price_history(self, token_id: str) -> dict[str, Any]:
        histories: dict[str, dict[str, Any]] = self._load("clob_prices_history.json")
        return histories.get(token_id, {"history": []})

    def tags(self) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        for event in self._load("gamma_events.json"):
            for tag in event["tags"]:
                seen[tag["slug"]] = tag
        return list(seen.values())

    def _load(self, name: str) -> Any:
        return json.loads((self._dir / name).read_text())


def build_source(settings: Settings, client: ReadOnlyClient | None) -> Source:
    if settings.source is SourceMode.FIXTURES:
        return FixtureSource(settings.fixtures_dir)
    if client is None:
        raise ValueError("Le mode live exige un ReadOnlyClient")
    return LiveSource(settings, client)
