"""Couche bronze : zone d'atterrissage brute, immuable et idempotente.

Disposition sur disque (format Hive, lisible directement par DuckDB) :

    data/bronze/<source>/<endpoint>/dt=YYYY-MM-DD/<run_id>.jsonl.gz   une ligne = un enregistrement
    data/bronze/_runs/<run_id>.json                                   manifeste de l'exécution

Règles :

- on stocke la **réponse brute** dans une enveloppe de métadonnées, sans la transformer ;
- un fichier écrit n'est jamais modifié (écriture atomique : fichier temporaire puis renommage) ;
- **idempotence** : `record_id = sha256(source | endpoint | clé | payload canonique)`. Un
  enregistrement identique déjà présent n'est pas réécrit. Relancer une ingestion sans
  changement côté source n'ajoute rien ;
- les fichiers bronze sont la **seule source de vérité** : l'entrepôt DuckDB est jetable et se
  reconstruit entièrement avec `make build`.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import tempfile
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_id(source: str, endpoint: str, key: str, payload: Any) -> str:
    digest = hashlib.sha256()
    for part in (source, endpoint, key, canonical_json(payload)):
        digest.update(part.encode())
        digest.update(b"\x1f")  # séparateur d'unité : pas de collision par concaténation
    return digest.hexdigest()


@dataclass(frozen=True)
class Envelope:
    record_id: str
    run_id: str
    ingested_at: str
    source: str
    endpoint: str
    record_key: str
    params: dict[str, Any]
    contract_ok: bool
    contract_errors: list[str]
    payload: Any


@dataclass
class RunManifest:
    run_id: str
    mode: str
    started_at: str
    finished_at: str | None = None
    status: str = "running"
    error: str | None = None
    counts: dict[str, dict[str, int]] = field(default_factory=dict)

    def count(self, stream: str, key: str, n: int = 1) -> None:
        bucket = self.counts.setdefault(stream, {"received": 0, "written": 0, "skipped": 0})
        bucket[key] = bucket.get(key, 0) + n


def new_run_id(now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    return f"{now:%Y%m%dT%H%M%SZ}-{os.urandom(3).hex()}"


class BronzeWriter:
    def __init__(self, bronze_dir: Path, run_id: str, now: datetime | None = None) -> None:
        self._dir = bronze_dir
        self._run_id = run_id
        self._now = now or datetime.now(UTC)
        self._known = existing_record_ids(bronze_dir)

    def write(
        self,
        source: str,
        endpoint: str,
        params: dict[str, Any],
        items: Iterable[tuple[str, Any, list[str]]],
        manifest: RunManifest,
    ) -> int:
        """Écrit les enregistrements nouveaux. `items` : (clé métier, payload, violations)."""
        stream = f"{source}.{endpoint}"
        lines: list[str] = []
        for key, payload, errors in items:
            manifest.count(stream, "received")
            rid = record_id(source, endpoint, key, payload)
            if rid in self._known:
                manifest.count(stream, "skipped")
                continue
            self._known.add(rid)
            env = Envelope(
                record_id=rid,
                run_id=self._run_id,
                ingested_at=self._now.isoformat(),
                source=source,
                endpoint=endpoint,
                record_key=key,
                params=params,
                contract_ok=not errors,
                contract_errors=errors,
                payload=payload,
            )
            lines.append(canonical_json(asdict(env)))
            manifest.count(stream, "written")

        if lines:
            partition = self._dir / source / endpoint / f"dt={self._now:%Y-%m-%d}"
            _atomic_append_file(partition, f"{self._run_id}.jsonl.gz", lines)
        return len(lines)


def write_manifest(bronze_dir: Path, manifest: RunManifest) -> Path:
    runs = bronze_dir / "_runs"
    runs.mkdir(parents=True, exist_ok=True)
    path = runs / f"{manifest.run_id}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(asdict(manifest), indent=2, ensure_ascii=False))
    tmp.replace(path)
    return path


def existing_record_ids(bronze_dir: Path) -> set[str]:
    files = [p for p in bronze_dir.glob("*/*/dt=*/*.jsonl.gz") if p.is_file()]
    if not files:
        return set()
    with duckdb.connect() as con:
        rows = con.execute(
            "select record_id from read_json(?, format='newline_delimited', "
            "columns={'record_id': 'VARCHAR'})",
            [[str(p) for p in files]],
        ).fetchall()
    return {r[0] for r in rows}


def _atomic_append_file(directory: Path, name: str, lines: list[str]) -> None:
    """Un même run peut écrire plusieurs fois dans une partition : on concatène des membres gzip
    (format valide, lu tel quel par DuckDB et gzip) en réécrivant atomiquement le fichier."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    previous = target.read_bytes() if target.exists() else b""
    data = gzip.compress(("\n".join(lines) + "\n").encode(), mtime=0)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".part")
    with os.fdopen(fd, "wb") as fh:
        fh.write(previous + data)
    Path(tmp).replace(target)
