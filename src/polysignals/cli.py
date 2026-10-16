"""Interface en ligne de commande : `uv run polysignals --help`."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import duckdb
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from polysignals import explain as ex
from polysignals.config import Settings, SourceMode, get_settings
from polysignals.doctor import diagnose
from polysignals.export import ExportError, build_export, write_export
from polysignals.http import ReadOnlyClient, ReadOnlyClientError
from polysignals.ingest import run_ingestion
from polysignals.sources import build_source

app = typer.Typer(
    help="Lire les marchés prédictifs Polymarket pour comprendre le contexte macro. "
    "Lecture seule : aucun pari, aucun wallet.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)
console = Console()

QUALITY_STYLE = {"solide": "green", "fragile": "yellow", "inexploitable": "red"}


def _settings(source: SourceMode | None = None) -> Settings:
    base = get_settings()
    return base.model_copy(update={"source": source}) if source else base


@app.callback()
def _main(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING, format="%(levelname)s %(message)s"
    )


@app.command()
def ingest(
    source: Annotated[
        SourceMode | None, typer.Option(help="live (API) ou fixtures (hors ligne)")
    ] = None,
) -> None:
    """Récupère les marchés de la watchlist et les écrit en bronze (idempotent)."""
    settings = _settings(source)
    console.print(f"▶ Ingestion [bold]{settings.source.value}[/] → {settings.bronze_dir}")
    try:
        with ReadOnlyClient(settings) as client:
            manifest = run_ingestion(settings, build_source(settings, client))
    except ReadOnlyClientError as exc:
        console.print(f"[red]✗ {exc}[/]")
        raise typer.Exit(1) from exc

    table = Table("Flux", "Reçus", "Écrits", "Déjà présents", title=f"Run {manifest.run_id}")
    for stream, c in manifest.counts.items():
        table.add_row(stream, str(c["received"]), str(c["written"]), str(c["skipped"]))
    console.print(table)


@app.command()
def watchlist() -> None:
    """Tableau de bord : les marchés macro suivis et la qualité de leur signal."""
    markets = _or_exit(lambda: ex.load_watchlist(get_settings().warehouse_path))
    table = Table("Thème", "Question  [dim](slug)[/]", "Proba", "7 j", "Signal", show_lines=True)
    for m in markets:
        table.add_row(
            m.theme_id,
            f"{m.question}\n[dim]{m.market_slug}[/]",
            ex.pct(m.implied_probability),
            ex.pts(m.change_7d),
            f"[{QUALITY_STYLE[m.signal_quality]}]{m.signal_quality}[/]",
        )
    console.print(table)
    if markets:
        console.print(
            f"[dim]Données au {markets[0].as_of:%d/%m/%Y %H:%M} UTC. "
            "Détail : polysignals explain <slug>[/]"
        )


@app.command()
def explain(
    market: Annotated[str, typer.Argument(help="slug ou identifiant du marché")],
    as_json: Annotated[bool, typer.Option("--json", help="sortie JSON brute")] = False,
) -> None:
    """Explique un marché pas à pas : ce qu'il dit, sa fiabilité, ce que ça change pour toi."""
    warehouse = get_settings().warehouse_path
    m = _or_exit(lambda: ex.find_market(warehouse, market))
    if m is None:
        console.print(f"[red]Marché introuvable dans la watchlist : {market}[/]")
        raise typer.Exit(1)
    if as_json:
        console.print_json(json.dumps(ex.to_dict(m), default=str, ensure_ascii=False))
        return

    series = ex.price_series(warehouse, m.market_id)
    console.print(Panel(f"[bold]{m.question}[/]\n[dim]{m.event_title} · {m.theme_label}[/]"))
    sections = [
        ("1. Ce que dit le marché", ex.what_market_says(m), "cyan"),
        ("2. Comment ça a bougé", ex.how_it_moved(m, series), "cyan"),
        ("3. Peut-on s'y fier ?", ex.can_we_trust_it(m), QUALITY_STYLE[m.signal_quality]),
        ("4. Et pour toi ?", ex.what_it_means_for_you(m), "magenta"),
    ]
    for title, lines, style in sections:
        console.print(Panel("\n".join(lines), title=title, title_align="left", border_style=style))


@app.command()
def export(
    out: Annotated[Path, typer.Option(help="fichier JSON de sortie")] = Path("web/data/gold.json"),
    run_results: Annotated[Path, typer.Option(help="run_results.json du dernier dbt build")] = Path(
        "transform/target/run_results.json"
    ),
    min_markets: Annotated[int, typer.Option(min=0)] = 1,
) -> None:
    """Exporte la couche gold en JSON pour le site (refusé si des tests dbt ont échoué)."""
    settings = get_settings()
    try:
        payload = build_export(settings.warehouse_path, settings.bronze_dir, run_results)
        write_export(payload, out, min_markets)
    except (ExportError, ex.WarehouseNotBuiltError) as exc:
        console.print(f"[red]✗ {exc}[/]")
        raise typer.Exit(1) from exc
    console.print(f"✓ {len(payload['markets'])} marchés exportés → {out}")


@app.command()
def doctor() -> None:
    """Diagnostic réseau : Polymarket est-il joignable (DNS, TLS, blocage ANJ) ?"""
    for d in diagnose(get_settings()):
        status = "[green]OK[/]" if d.tls_ok else "[red]KO[/]"
        console.print(f"{status} {d.host}  [dim]{', '.join(d.addresses) or '—'}[/]\n   {d.detail}")
        if d.likely_blocked:
            console.print(
                "   [yellow]→ Blocage ANJ probable : le DNS de ton fournisseur redirige ce nom.\n"
                "     Voir docs/runbook.md § « Accès aux données live ». Le mode fixtures "
                "reste disponible hors ligne (make demo).[/]"
            )


@app.command()
def tags(
    search: Annotated[str | None, typer.Option(help="filtre sur le slug ou le libellé")] = None,
    source: Annotated[SourceMode | None, typer.Option()] = None,
) -> None:
    """Liste les tags Gamma, pour choisir les sélecteurs de la watchlist."""
    settings = _settings(source)
    with ReadOnlyClient(settings) as client:
        try:
            items = build_source(settings, client).tags()
        except ReadOnlyClientError as exc:
            console.print(f"[red]✗ {exc}[/]")
            raise typer.Exit(1) from exc
    needle = (search or "").lower()
    table = Table("slug", "libellé")
    for t in sorted(items, key=lambda t: str(t.get("slug"))):
        slug, label = str(t.get("slug", "")), str(t.get("label", ""))
        if needle in slug.lower() or needle in label.lower():
            table.add_row(slug, label)
    console.print(table)


@app.command()
def runs(limit: Annotated[int, typer.Option(min=1)] = 10) -> None:
    """Derniers runs d'ingestion (statut, durée, volumes)."""
    files = sorted(get_settings().bronze_dir.glob("_runs/*.json"), reverse=True)[:limit]
    table = Table("Run", "Mode", "Statut", "Écrits", "Déjà présents", "Erreur")
    for f in files:
        r = json.loads(f.read_text())
        written = sum(c.get("written", 0) for c in r["counts"].values())
        skipped = sum(c.get("skipped", 0) for c in r["counts"].values())
        style = "green" if r["status"] == "success" else "red"
        table.add_row(
            r["run_id"],
            r["mode"],
            f"[{style}]{r['status']}[/]",
            str(written),
            str(skipped),
            r.get("error") or "",
        )
    console.print(table)


@app.command()
def contracts() -> None:
    """Liste les enregistrements bronze qui violent leur contrat de données."""
    files = [str(p) for p in get_settings().bronze_dir.glob("*/*/dt=*/*.jsonl.gz")]
    if not files:
        console.print("Aucune donnée bronze.")
        return
    rows = duckdb.execute(
        "select source || '.' || endpoint, record_key, contract_errors "
        "from read_json(?, format='newline_delimited', columns={source: 'VARCHAR', "
        "endpoint: 'VARCHAR', record_key: 'VARCHAR', contract_ok: 'BOOLEAN', "
        "contract_errors: 'JSON'}) where not contract_ok",
        [files],
    ).fetchall()
    if not rows:
        console.print("[green]✓ Tous les enregistrements respectent leur contrat.[/]")
        return
    table = Table("Flux", "Clé", "Violations")
    for stream, key, errors in rows:
        table.add_row(stream, key, "\n".join(json.loads(errors)))
    console.print(table)
    raise typer.Exit(1)


def _or_exit[T](fn: Callable[[], T]) -> T:
    try:
        return fn()
    except ex.WarehouseNotBuiltError as exc:
        console.print(f"[red]✗ {exc}[/]")
        raise typer.Exit(1) from exc
