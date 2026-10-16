from __future__ import annotations

import contextlib
import gzip
import json
from datetime import UTC, datetime

from polysignals.bronze import BronzeWriter, RunManifest, record_id
from polysignals.config import Settings
from polysignals.ingest import run_ingestion
from polysignals.sources import FixtureSource

NOW = datetime(2026, 10, 14, 8, 0, tzinfo=UTC)


def test_record_id_is_canonical() -> None:
    assert record_id("s", "e", "k", {"a": 1, "b": 2}) == record_id("s", "e", "k", {"b": 2, "a": 1})


def test_record_id_has_no_concatenation_collision() -> None:
    assert record_id("ab", "c", "k", 1) != record_id("a", "bc", "k", 1)


def test_ingestion_is_idempotent(settings: Settings) -> None:
    source = FixtureSource(settings.fixtures_dir)
    first = run_ingestion(settings, source, NOW)
    second = run_ingestion(settings, source, NOW)

    assert first.counts["gamma.events"]["written"] == 4  # l'événement clos est filtré
    assert first.counts["clob.prices_history"]["written"] == 6
    assert all(c["written"] == 0 for c in second.counts.values())
    assert second.status == "success"


def test_written_files_are_valid_gzip_jsonl(settings: Settings) -> None:
    run_ingestion(settings, FixtureSource(settings.fixtures_dir), NOW)
    files = list(settings.bronze_dir.glob("gamma/events/dt=2026-10-14/*.jsonl.gz"))
    assert len(files) == 1
    lines = gzip.decompress(files[0].read_bytes()).decode().splitlines()
    envelope = json.loads(lines[0])
    assert {"record_id", "run_id", "ingested_at", "contract_ok", "payload"} <= envelope.keys()


def test_multiple_writes_in_one_run_append_gzip_members(settings: Settings) -> None:
    writer = BronzeWriter(settings.bronze_dir, "run-1", NOW)
    manifest = RunManifest(run_id="run-1", mode="test", started_at=NOW.isoformat())
    writer.write("s", "e", {}, [("a", {"v": 1}, [])], manifest)
    writer.write("s", "e", {}, [("b", {"v": 2}, [])], manifest)
    path = settings.bronze_dir / "s/e/dt=2026-10-14/run-1.jsonl.gz"
    assert len(gzip.decompress(path.read_bytes()).decode().splitlines()) == 2


def test_failed_run_still_writes_manifest(settings: Settings) -> None:
    class Broken(FixtureSource):
        def price_history(self, token_id: str) -> dict[str, object]:
            raise RuntimeError("API en panne")

    with contextlib.suppress(RuntimeError):
        run_ingestion(settings, Broken(settings.fixtures_dir), NOW)
    manifest = json.loads(next(settings.bronze_dir.glob("_runs/*.json")).read_text())
    assert manifest["status"] == "failed"
    assert "API en panne" in manifest["error"]
