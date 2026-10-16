---
type: session-context
project: polymarket-signals
updated: 2026-10-15
---

## Statut : 🟢 Actif — v0.2 (site web + pipeline quotidien) prête, NON poussée

**Dernière session :** 2026-10-15
**Prochaine étape :** confirmer avec Adrien : (1) dépôt GitHub PUBLIC `AdrienCasse/polymarket-signals` (Pages gratuit seulement en public), (2) identité git des commits (gmail perso vs noreply `128650043+AdrienCasse@users.noreply.github.com`). Puis commit initial, push, `gh api repos/AdrienCasse/polymarket-signals/pages -X POST -f build_type=workflow`, `gh workflow run pipeline.yml`, vérifier slugs de tags et contrats au 1er run.

## Ce qui a été fait
- Projet créé (`git init`, rien de commité) : uv + Python 3.12, `src/polysignals/`, `transform/` (dbt-duckdb), `academy/`, `docs/`, CI GitHub Actions, Dependabot
- Ingestion lecture seule : `http.py` (GET, liste blanche, TLS, sans redirection, taille bornée, débit limité, backoff), `models.py` (contrats pydantic), `bronze.py` (JSONL.gz Hive, empreinte sha256, écriture atomique, manifestes `_runs/`), `sources.py` (live | fixtures), `ingest.py`
- dbt : silver (`stg_*`, `int_*`), gold (`dim_markets`, `fct_market_snapshots`, `fct_daily_prices`, `mart_macro_watchlist` avec contrat appliqué), 60 tests dont un test unitaire de la règle de probabilité implicite, exposures (CLI, fintrack prévu)
- CLI : `ingest`, `watchlist`, `explain`, `doctor`, `tags`, `runs`, `contracts`
- Fixtures synthétiques reproductibles (`tests/fixtures/generate.py`)
- Tests : 26 pytest (dont e2e fixtures → dbt build) ; `make check` vert (ruff, mypy strict, pytest, pip-audit)
- Académie : 7 leçons (00 architecture → 06 cadre légal) ; sous-agents `macro-tutor` et `bias-analyst`

- v0.2 : site Next.js 16 statique (`web/` : tableau de bord, page marché en 4 temps, Académie + simulateur d'écart, Sous le capot), `polysignals export` → `web/data/gold.json` (refusé si tests dbt KO ou 0 marché), workflow `pipeline.yml` (cron 05:17 UTC : ingest live → branche orpheline `data` → dbt → export → Pages OIDC), `ci.yml` = `make check` (Python + web). Démo séparée dans `data-demo/`. 30 tests pytest, make check vert. Captures headless vérifiées (desktop + mobile)

## Décisions récentes
- Stack DuckDB + dbt + bronze en fichiers ; lecture seule par construction ; watchlist = seed dbt unique (détail dans decisions.md)
- Agents : profiler les biais (calibration mesurée), pas de « tips » de pari ; MCP maison lecture seule plutôt qu'un MCP tiers

## Questions ouvertes
- Accès live : résolu par l'ingestion GitHub Actions (validé par Adrien le 2026-10-15)
- Slugs de tags (`fed-rates`, `ecb`, `inflation`, `recession`) non vérifiés sur l'API réelle
- Format réel de Gamma/CLOB à confronter aux contrats au premier run live
- Études sur le biais favori/outsider sur Polymarket (arXiv 2606.04217, 2602.19520, thèse Princeton) : à lire avant la v0.3 calibration
- `behavior-coach` (biais personnels) côté fintrack : à proposer dans ce projet-là
